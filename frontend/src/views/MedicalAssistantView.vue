<template>

    <nav :class="{ hidden: isSidebarHidden }" id="sidebar">
        <div class="float-top">
            <div class="sidebar-controls">
                <button class="new-chat" @click="startNewChat"><i class="fa fa-plus"></i> New
                    chat</button>
                <button class="hide-sidebar" @click="toggleSidebar"><i class="fa fa-chevron-left"></i></button>
            </div>
            <ul v-if="user && user.chats && user.chats.length" class="conversations">

                <li v-for="c in user.chats" :key="c.chat_id"
                    :class="{ active: c.chat_id === parseInt(currentChat.chat_id) }">
                    <button class="conversation-button" @click="navigateToChat(c.chat_id)">
                        {{ c.title || 'Untitled Chat' }}
                    </button>
                </li>
            </ul>
            <ul v-else="user && user.chats && user.chats.length">

            </ul>
        </div>
        <div class="user-menu">
            <button @click="handleLogout">Logout</button>
        </div>
    </nav>

    <main>
        <div v-if="activeView" class="view conversation-view">

            <div v-for="(entry, index) in currentChat.messages" :key="index" class="chat-message">

                <div class="user message">
                    <div class="identity"><i class="user-icon">USER</i></div>
                    <div class="content">
                        <p>{{ entry.question }}</p>
                    </div>
                </div>
                <div class="assistant message">
                    <div class="identity"><i class="gpt user-icon">RAG</i></div>
                    <div class="content">
                        <p v-if="entry.answer" v-html="compiledMarkdown(entry.answer)" class="markdown-output"></p>
                        <p v-else class="blinking">...</p>
                    </div>
                </div>
            </div>
        </div>

        <div v-else class="view new-chat-view">
            <div class="model-selector">
                <h1>Medical Assistant RAG</h1>
            </div>
        </div>



        <div id="message-form">
            <div class="message-wrapper">
                <textarea id="message" rows="1" v-model="query" placeholder="Ask a Medical Question..."
                    @input="resizeTextarea" ref="messageBox"></textarea>
                <button class="send-button" @click="sendMessage"><i class="fa fa-paper-plane"></i></button>
            </div>
            <div class="disclaimer">
                This is a Medical Assistant RAG for personal use and educational purposes only.
            </div>
        </div>
    </main>

</template>

<script>
import { getCookie } from '@/store'
import { mapActions, mapMutations, mapState } from 'vuex'
import { marked } from 'marked'

export default {
    name: "Assistant",
    data() {
        return {
            query: '',
            currentChat: {
                chat_id: null,
                title: null,
                messages: []
            },
            loading: false,
            isSidebarHidden: false,
            // activeView: "conversation-view",


        };
    },
    computed: {
        ...mapState(['user']),
        chatId() {

            return this.$route.params.chatId ? this.$route.params.chatId : null
        },
        activeView() {
            return this.currentChat.messages.length > 0 || this.loading
        },
    },
    async created() {
        const toDo = this.$route.params.chatId
        if (toDo) {
            this.loading = true
            await this.fetchChat()
            this.loading = false
        }
    },
    methods: {
        ...mapMutations(['ADD_CHAT_TO_USER']),
        ...mapActions(['logout']),
        async handleLogout() {
            await this.logout();
            this.$router.push('/login');
        },
        toggleSidebar() {
            this.isSidebarHidden = !this.isSidebarHidden;
        },
        compiledMarkdown(text) {
            return marked(text || '')
        },
        resizeTextarea() {
            const el = this.$refs.messageBox;
            el.style.height = "auto";
            el.style.height = Math.min(el.scrollHeight + 2, 200) + "px";
        },
        async fetchChat() {
            try {
                const token = getCookie('csrf_access_token')
                const res = await fetch(`http://localhost:5000/chat/${this.chatId}`, {
                    method: 'GET',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-Token': token
                    }
                })

                const data = await res.json()
                if (!res.ok) throw new Error(data.error || 'Unknown error')

                this.currentChat = data

            } catch (err) {
                console.error(err)
            }
        },

        async sendMessage() {
            const userQuery = this.query.trim()
            if (!userQuery) return

            // Remove previous error message if present
            const lastMsg = this.currentChat.messages.at(-1)
            if (lastMsg && !lastMsg.message_id && lastMsg.answer?.startsWith('[Error:')) {
                this.currentChat.messages.pop()
            }

            // Add temporary message
            this.currentChat.messages.push({
                message_id: null,
                question: userQuery,
                answer: null
            })

            this.query = ''
            this.loading = true

            try {
                const token = getCookie('csrf_access_token')
                if (!token) throw new Error('CSRF token missing')

                const endpoint = this.chatId
                    ? `http://localhost:5000/chat/${this.chatId}`
                    : `http://localhost:5000/chat/new`

                const res = await fetch(endpoint, {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-Token': token
                    },
                    body: JSON.stringify({ query: userQuery })
                })

                const data = await res.json()
                if (!res.ok) {
                    this.loading = false
                    throw new Error(data.error || 'Unknown error')

                }

                console.log('Checkpoint 1')
                if (this.chatId) {
                    this.currentChat.messages[this.currentChat.messages.length - 1].message_id = data.message_id
                    this.currentChat.messages[this.currentChat.messages.length - 1].answer = data.answer
                    console.log('Checkpoint 2')
                } else {
                    console.log('Checkpoint 3')
                    console.log(data.messages);

                    this.currentChat.messages.splice(-1, 1, {
                        message_id: data.messages[data.messages.length - 1].message_id,
                        question: userQuery,
                        answer: data.messages[data.messages.length - 1].answer
                    })


                    this.ADD_CHAT_TO_USER({
                        chat_id: data.chat_id,
                        title: data.title
                    })

                    this.currentChat.chat_id = data.chat_id
                    this.currentChat.title = data.title

                }


            } catch (err) {
                console.error(err)
                this.currentChat.messages.splice(-1, 1, {
                    message_id: null,
                    question: userQuery,
                    answer: `[Error: ${err.message}]`
                })
            } finally {
                this.loading = false
            }
        },
        async navigateToChat(cID) {

            await this.$router.replace({ name: 'ChatById', params: { chatId: cID } })
        },

        startNewChat() {
            this.$router.replace({ name: 'NewChat' })
            this.currentChat = {
                chat_id: null,
                title: null,
                messages: []
            }
        }
    }
};
</script>


<style scoped>
#sidebar {
    position: relative;
    left: 0;
    background: var(--color-3);
    width: 25%;
    padding: 0.5rem;
    box-sizing: border-box;
    display: flex;
    justify-content: space-between;
    flex-direction: column;
    transition: all 0.2s ease-in-out;
}

.float-top {
    display: flex;
    flex-direction: column;
    height: calc(100% - 50px);
}

#sidebar.hidden {
    left: -25%;
    margin-right: -25%;
}

#sidebar.hidden .hide-sidebar {
    left: 60px;
    transform: rotate(180deg);
    padding: 15px 13px 11px 13px;
}

button {
    display: block;
    background: inherit;
    border: 1px solid var(--color-16);
    border-radius: 5px;
    color: var(--color-1);
    padding: 13px;
    box-sizing: border-box;
    text-align: left;
    cursor: pointer;
}

button:hover {
    background: var(--color-4);
}

.sidebar-controls {
    display: flex;
    gap: 10px;
    margin-bottom: 8px;
}

.sidebar-controls button {
    padding: 12px 13px 12px 13px;
}

.hide-sidebar {
    position: relative;
    left: 0;
    top: 0;
    transition: all 0.2s ease-in-out;
    transform: rotate(0deg);
}

.new-chat i {
    margin-right: 13px;
}

.new-chat {
    flex: 1;
}

.conversations {
    width: calc(100% + 8px);
    overflow-y: scroll;
}

.conversations,
.conversations li {
    list-style: none;
    list-style-type: none;
    margin: 0;
    padding: 0;
}

.conversations li {
    position: relative;
}

.conversations li>button {
    width: 100%;
    border: none;
    font-size: 0.9em;
    white-space: nowrap;
    overflow: hidden;
}

.conversations li.active>button {
    background: var(--color-2);
}

.conversations li.grouping {
    color: var(--color-6);
    font-size: 0.7em;
    font-weight: bold;
    padding-left: 13px;
    margin-top: 12px;
    margin-bottom: 12px;
}

.user-icon {
    padding: 6px;
    color: var(--color-1);
    background: var(--color-5);
    display: inline-block;
    text-align: center;
    width: fit-content;
    border-radius: 3px;
    margin-right: 6px;
    font-style: normal;
    height: 18px;
    font-size: 15px;
    text-transform: uppercase;
    font-family: system-ui, sans-serif;
}

.gpt.user-icon {
    background: var(--color-7);
}

.user-menu {
    position: relative;
}

::-webkit-scrollbar {
    width: 9px;
}

::-webkit-scrollbar-track {
    background-color: transparent;
}

::-webkit-scrollbar-thumb {
    background-color: transparent;
}

:hover::-webkit-scrollbar-thumb {
    background-color: var(--color-10)c3;
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background-color: var(--color-10);
    border-radius: 5px;
}

main {
    width: 100%;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    align-content: center;
    justify-content: space-between;
    padding: 0 0 30px 0;
    box-sizing: border-box;
}

main .view {
    display: flex;
    flex-direction: column;
}

.model-selector {
    position: relative;
    border-radius: 11px;
    background: var(--color-3);
    display: flex;
    padding: 0.25rem;
    gap: 4px;
    margin: 1.5rem auto;
    z-index: 2;
    border: 5px solid var(--color-16);
}

.model-selector>h1 {
    color: var(--color-1);
    padding: 0 0.5rem;
}

p.secondary {
    font-size: 1em;
    color: var(--color-12);
}

.view.conversation-view {

    overflow-y: auto;
}

.message {
    display: flex;
    gap: 1.2rem;
    padding: 1.5rem 3.7rem 0.95rem 3.7rem;
    border-bottom: 1px solid var(--color-19);
    font-size: 1rem;
}

.message .content {
    padding-top: 5px;
}

.user.message {
    color: var(--color-10);
}

.assistant.message {
    background: var(--color-13);
    color: var(--color-14);
}

#message-form {
    margin: 0 auto;
    width: 100%;
    box-sizing: border-box;
    max-width: 850px;
    text-align: center;
    padding: 0px 2.5rem 0 2.5rem;
    box-shadow: var(--color-2) 0 0 50px;
}

.message-wrapper {
    position: relative;
}

#message::placeholder {
    color: var(--color-6);
}

#message {
    background: var(--color-9);
    border-radius: 13px;
    width: 100%;
    box-sizing: border-box;
    border: 1px solid var(--color-20);
    resize: none;
    padding: 17px 85px 17px 15px;
    font-family: inherit;
    font-size: 1em;
    color: var(--color-1);
    box-shadow: rgba(0, 0, 0, 0.2) 0 0 45px;
    outline: none;
}

.disclaimer {
    margin-top: 12px;
    color: var(--color-15);
    font-size: 0.7em;
}

.send-button {
    position: absolute;
    right: 15px;
    top: 50%;
    transform: translateY(-50%);
    background: var(--color-11);
    border-radius: 5px;
    display: inline-block;
    font-size: 1em;
    padding: 7px 9px 7px 7px;
    color: var(--color-1);
    border: none;
    margin-top: -2px;
}

button.send-button:hover {
    border: none;
    background: var(--color-11);
    color: var(--color-1);
}

p {
    margin: 0 0 1.5em 0;
}


.markdown-output {
  line-height: 1.3;
  padding: 0; /* no padding to interfere with margin collapsing */
  white-space: pre-wrap;
}

/* Paragraphs */
.markdown-output p {
  margin: 0;
  margin-top: 0.5rem;
  text-indent: 0;
}

/* Headings with only top margins */
.markdown-output h1 {
  font-size: 1.3rem;
  margin: 1rem 0 0 0;
}

.markdown-output h2 {
  font-size: 1.15rem;
  margin: 0.75rem 0 0 0;
}

.markdown-output h3 {
  font-size: 1.05rem;
  margin: 0.6rem 0 0 0;
}

/* Lists */
.markdown-output ul,
.markdown-output ol {
  margin: 0;
  margin-top: 0.5rem;
  padding-left: 1.2rem;
}

.markdown-output li {
  margin: 0.25rem 0 0 0;
}

/* Bold text */
.markdown-output strong {
  font-weight: 600;
}

/* Code */
.markdown-output pre,
.markdown-output code {
  background-color: #f6f8fa;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.95rem;
  margin-top: 0.5rem;
}

/* Blockquotes */
.markdown-output blockquote {
  border-left: 3px solid #ccc;
  padding-left: 0.75rem;
  margin: 0;
  margin-top: 0.75rem;
  color: #555;
  font-style: italic;
}
</style>