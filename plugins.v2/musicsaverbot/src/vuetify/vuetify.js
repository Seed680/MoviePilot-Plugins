// Utilities
import { createVuetify } from 'vuetify'

// Icons
import { mdi } from 'vuetify/iconsets/mdi'

// Styles
import 'vuetify/styles'

export const vuetify = createVuetify({
  icons: {
    defaultSet: 'mdi',
    sets: {
      mdi,
    },
  },
  theme: {
    themes: {
      light: {
        colors: {
          primary: '#1867C0',
          secondary: '#5CBBF6',
        },
      },
    },
  },
})