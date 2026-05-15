"""
CloakBrowser 辅助类 - 用于绕过反机器人检测
完全兼容 Playwright API，只需修改导入语句即可使用
GitHub: https://github.com/CloakHQ/CloakBrowser
"""
from typing import Optional, Callable, Any
import uuid

from app.core.config import settings
from app.log import logger


class CloakBrowserHelper:
    """
    CloakBrowser 辅助类
    提供与 PlaywrightHelper 兼容的接口，但使用 CloakBrowser 实现
    """
    
    def __init__(self):
        self._browser = None
        self._context = None
        self._page = None
    
    def get_page_source(self, url: str,
                        cookies: Optional[str] = None,
                        ua: Optional[str] = None,
                        proxies: Optional[dict] = None,
                        headless: Optional[bool] = False,
                        timeout: Optional[int] = 60) -> Optional[str]:
        """
        获取网页源码
        :param url: 网页地址
        :param cookies: cookies
        :param ua: user-agent
        :param proxies: 代理
        :param headless: 是否无头模式
        :param timeout: 超时时间
        :return: 页面源码
        """
        source = None
        
        try:
            # 尝试导入 cloakbrowser
            from cloakbrowser import launch
            
            logger.debug(f"使用 CloakBrowser 访问: {url}")
            
            # 启动浏览器（默认启用 humanize 以模拟真人行为）
            browser = launch(
                headless=headless,
                humanize=True  # 启用人类行为模拟
            )
            
            try:
                # 创建新页面
                page = browser.new_page()
                
                try:
                    # 设置 User-Agent
                    if ua:
                        page.set_extra_http_headers({"user-agent": ua})
                    
                    # 设置 Cookies
                    if cookies:
                        # 解析 cookie 字符串并设置
                        cookie_list = self._parse_cookies(cookies, url)
                        if cookie_list:
                            context = page.context
                            context.add_cookies(cookie_list)
                    
                    # 访问页面
                    page.goto(url, timeout=timeout * 1000, wait_until="networkidle")
                    
                    # 等待页面加载完成
                    page.wait_for_load_state("networkidle", timeout=timeout * 1000)
                    
                    # 获取页面源码
                    source = page.content()
                    logger.debug(f"成功获取页面源码，长度: {len(source)}")
                    
                except Exception as e:
                    logger.error(f"CloakBrowser 页面操作失败: {str(e)}")
                finally:
                    # 关闭页面
                    try:
                        page.close()
                    except:
                        pass
                        
            finally:
                # 关闭浏览器
                try:
                    browser.close()
                except:
                    pass
                    
        except ImportError:
            logger.warning("未安装 cloakbrowser，回退到 Playwright")
            # 如果未安装 cloakbrowser，回退到 Playwright
            return self._fallback_to_playwright(url, cookies, ua, proxies, headless, timeout)
        except Exception as e:
            logger.error(f"CloakBrowser 初始化失败: {str(e)}")
            # 出错时回退到 Playwright
            return self._fallback_to_playwright(url, cookies, ua, proxies, headless, timeout)
        
        return source
    
    def action(self, url: str,
               callback: Callable,
               cookies: Optional[str] = None,
               ua: Optional[str] = None,
               proxies: Optional[dict] = None,
               headless: Optional[bool] = False,
               timeout: Optional[int] = 60) -> Any:
        """
        访问网页，接收Page对象并执行操作
        :param url: 网页地址
        :param callback: 回调函数，需要接收page对象
        :param cookies: cookies
        :param ua: user-agent
        :param proxies: 代理
        :param headless: 是否无头模式
        :param timeout: 超时时间
        :return: 回调函数的返回值
        """
        result = None
        
        try:
            # 尝试导入 cloakbrowser
            from cloakbrowser import launch
            
            logger.debug(f"使用 CloakBrowser 执行操作: {url}")
            
            # 启动浏览器
            browser = launch(
                headless=headless,
                humanize=True
            )
            
            try:
                # 创建新页面
                page = browser.new_page()
                
                try:
                    # 设置 User-Agent
                    if ua:
                        page.set_extra_http_headers({"user-agent": ua})
                    
                    # 设置 Cookies
                    if cookies:
                        cookie_list = self._parse_cookies(cookies, url)
                        if cookie_list:
                            context = page.context
                            context.add_cookies(cookie_list)
                    
                    # 访问页面
                    page.goto(url, timeout=timeout * 1000, wait_until="networkidle")
                    page.wait_for_load_state("networkidle", timeout=timeout * 1000)
                    
                    # 执行回调函数
                    result = callback(page)
                    
                except Exception as e:
                    logger.error(f"CloakBrowser action 操作失败: {str(e)}")
                finally:
                    try:
                        page.close()
                    except:
                        pass
                        
            finally:
                try:
                    browser.close()
                except:
                    pass
                    
        except ImportError:
            logger.warning("未安装 cloakbrowser，回退到 Playwright")
            # 回退逻辑需要在外部处理
            raise ImportError("cloakbrowser not available")
        except Exception as e:
            logger.error(f"CloakBrowser action 初始化失败: {str(e)}")
            raise
        
        return result
    
    @staticmethod
    def _parse_cookies(cookie_str: str, url: str) -> list:
        """
        解析 cookie 字符串为列表格式
        :param cookie_str: cookie 字符串
        :param url: URL 用于提取 domain
        :return: cookie 列表
        """
        cookies = []
        if not cookie_str:
            return cookies
        
        try:
            # 从 URL 提取域名
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # 解析 cookie 字符串 (name=value; name2=value2)
            for item in cookie_str.split(';'):
                item = item.strip()
                if '=' in item:
                    name, value = item.split('=', 1)
                    cookies.append({
                        'name': name.strip(),
                        'value': value.strip(),
                        'domain': domain,
                        'path': '/'
                    })
        except Exception as e:
            logger.error(f"解析 cookies 失败: {str(e)}")
        
        return cookies
    
    @staticmethod
    def _fallback_to_playwright(url: str,
                                 cookies: Optional[str],
                                 ua: Optional[str],
                                 proxies: Optional[dict],
                                 headless: Optional[bool],
                                 timeout: Optional[int]) -> Optional[str]:
        """
        回退到 Playwright 实现
        """
        try:
            from app.helper.browser import PlaywrightHelper
            logger.info("使用 PlaywrightHelper 作为后备方案")
            return PlaywrightHelper().get_page_source(
                url=url,
                cookies=cookies,
                ua=ua,
                proxies=proxies,
                headless=headless,
                timeout=timeout
            )
        except Exception as e:
            logger.error(f"Playwright 回退也失败: {str(e)}")
            return None
