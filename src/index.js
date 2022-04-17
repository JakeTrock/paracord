import App from './App.vue'
import {createApp, withDirectives} from 'vue'

require('normalize.css/normalize.css')
require('./styles/index.scss')

const app = createApp(App);

// Focus element
withDirectives('focus', {
  inserted: function (el) {
    el.focus()
  }
})

app.mount('#app');