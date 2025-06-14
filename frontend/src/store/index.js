import { createStore } from 'vuex'

const state = {
  user: null
}

const mutations = {
  SET_USER(state, user) {
    state.user = user
  },
  ADD_CHAT_TO_USER(state, chat) {
    if (!state.user.chats.some(c => c.chat_id === chat.chat_id)) {

      state.user.chats.unshift(chat)
    }
  }
}

const actions = {
  async init({ commit, dispatch }) {
    const getUser = async (csrfToken) => {
      try {
        const res = await fetch('http://localhost:5000/user/', {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken
          }
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.error || 'Failed to fetch user');
        }

        return await res.json();
      } catch (err) {
        console.error('Failed to fetch user:', err);
        return null;
      }
    };

    const tryFetchUser = async (token) => {
      const user = await getUser(token);
      if (user) commit('SET_USER', user);
    };

    const csrfAccessToken = getCookie('csrf_access_token');
    if (csrfAccessToken) {
      await tryFetchUser(csrfAccessToken);
      return;
    }

    const csrfRefreshToken = getCookie('csrf_refresh_token');
    if (csrfRefreshToken) {
      try {
        await dispatch('refreshToken');
        const newToken = getCookie('csrf_access_token');
        if (newToken) await tryFetchUser(newToken);
      } catch (err) {
        console.error('Error loading user data:', err);
      }
    }
  }

  ,
  async register(_, userData) {
    const res = await fetch('http://localhost:5000/user/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        email: userData.email,
        name: userData.name
      })
    })

    const response = await res.json()
    if (!res.ok) throw new Error(response.error || 'Registration failed')

    return true
  },
  async login(_, data) {
    const res = await fetch('http://localhost:5000/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        email: data.email
      })
    })

    const response = await res.json()
    if (!res.ok) throw new Error(response.error)

    return true

  },

  async logout(_) {
    try{
      const res = await fetch('http://localhost:5000/auth/logout', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'X-CSRF-Token': getCookie('csrf_access_token')
      }
    })

    if (!res.ok) {
      const response = await res.json()
      throw new Error(response.error || 'Logout failed')
    }

    return true
    }
    catch (error) {
      console.error('Logout error:', error);
    }
  },

  async refreshToken(_) {
    const res = await fetch('http://localhost:5000/auth/refresh', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'X-CSRF-Token': getCookie('csrf_refresh_token')
      }
    })
    if (!res.ok) {
      const response = await res.json()
      throw new Error(response.error || 'Refresh failed')
    }

    return true
  }
}

const getters = {
  getUser: state => state.user
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export { getCookie }

const store = createStore({
  state,
  mutations,
  actions,
  getters
})

export default store
