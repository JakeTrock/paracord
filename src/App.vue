<template>
  <div class="container">
    <div id="app" class="row">
      <div class="col-xl-8 col-lg-12 col-md-6 col-sm-12 col-12">
        <div class="panel panel-info">
          <div class="panel-heading">
            <h2>{{ room }} in {{ channel }}</h2>
            <span class="badge">{{ Object.keys(members).length }}</span> Members online:
            <span v-for="member in members">{{ member.username }}</span>
          </div>
          <div class="panel-body">
            <div v-if="joined">
              <em>
                <span v-text="status"></span>
              </em>
              <div class="chat-wrapper" ref="chatWrapper">
                <ul class="chat">
                  <li class="left clearfix" v-for="message in messages[channel][room]">
                    <div class="chat-body clearfix">
                      <div class="header">
                        <strong class="primary-font">{{ message.username }}</strong>
                      </div>
                      <p>{{ message.message }}</p>
                    </div>
                  </li>
                </ul>
              </div>
              <div class="panel-footer">
                <span v-for="user in usersTyping">
                  <p>{{ user }} is typing</p>
                </span>
                <div class="input-group">
                  <input
                    id="btn-input"
                    type="text"
                    name="message"
                    class="form-control input-sm"
                    placeholder="Type your message here..."
                    v-model="newMessage"
                    ref="messageInputField"
                    @change="typingIndicator"
                    @keyup.enter="sendMessage"
                  />
                  <input type="file" id="btn-upld" />
                  <span class="input-group-btn">
                    <button class="btn btn-primary btn-sm" id="btn-chat" @click="sendMessage">Send</button>
                  </span>
                </div>
                <br />
                <div class="input-group">
                  Members :
                  <span v-for="member in members">
                    <b>{{ member }}</b>,
                  </span>
                </div>
                <button class="btn btn-primary btn-sm" id="btn-wrtc" @click="initRTC">Join VC</button>
              </div>
            </div>
            <div v-else>
              <div class="form-group">
                <label>Room Name</label>
                <input
                  type="text"
                  class="form-control"
                  placeholder="chat room name"
                  v-model="room"
                  @keyup.enter="joinChat"
                />
              </div>
              <div class="form-group">
                <label>Username</label>
                <input
                  type="text"
                  class="form-control"
                  placeholder="enter your username to join chat"
                  v-model="username"
                  @keyup.enter="joinChat"
                />
              </div>
              <button class="btn btn-primary" @click="joinChat">JOIN</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const Peer = require('simple-peer');
const P2PT = require('p2pt');

//https://gist.github.com/jed/982883
// function b(a) { return a ? (a ^ Math.random() * 16 >> a / 4).toString(16) : ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, b) }
function b() { return "tahiti" }

module.exports = {
  data() {
    return {
      joined: false,
      room: b(),
      channel: 'main',
      username: '',
      members: {},
      newMessage: '',
      typing: false,
      messages: {},
      usersTyping: [],
      status: ''
    }
  },

  methods: {
    init() {
      this.peers = {};

      let announceURLs = [
        "wss://tracker.openwebtorrent.com",
        "wss://tracker.sloppyta.co:443/announce",
        "wss://tracker.novage.com.ua:443/announce",
        "wss://tracker.btorrent.xyz:443/announce",
      ]
      if (window.location.hostname === "localhost") {
        announceURLs = ["ws://localhost:5000"]
      }

      this.p2pt = new P2PT(announceURLs, 'p2chat' + this.room)
    },

    joinChat() {
      if (this.room.trim() === '' || this.username.trim() === '') {
        return
      }

      this.init()
      this.joined = true
      this.status = `${this.username} joined the chat`
      this.usernames = {}

      this.listen()
    },

    typingIndicator() {
      if (this.newMessage.trim() !== '') {
        if (this.typing) return;
        const message = {
          type: "msg-typing-start",
          username: this.username
        }

        this.typing = true;

        for (var key in this.peers) {
          this.p2pt.send(this.peers[key], JSON.stringify(message))
        }
      } else {
        const message = {
          type: "msg-typing-stop",
          username: this.username
        }

        this.typing = false;

        for (var key in this.peers) {
          this.p2pt.send(this.peers[key], JSON.stringify(message))
        }
      }
    },

    initRtc() {
      //TODO: serverless RTC
    },

    sendMessage() {
      if (this.newMessage.trim() === '') {
        return
      }

      const message = {
        type: "msg-plaintext",
        timestamp: Date.now(),
        room: this.room,
        channel: this.channel, //TODO: do sumthin bout it!!(add visual sorting)
        username: this.username,
        message: this.newMessage
      }

      const upb = document.getElementById("btn-upld")
      if (upb.files.length > 0) {
        message.files = uploadButton.files;//TODO: you need to check if this would work and properly send the whole chunk
      }

      const stopTyping = {
        type: "msg-typing-stop",
        username: this.username
      }

      this.typing = false;

      // Clear input field
      this.newMessage = '';

      for (var key in this.peers) {
        this.p2pt.send(this.peers[key], JSON.stringify(message))
        this.p2pt.send(this.peers[key], JSON.stringify(stopTyping))
      }

      if (!(this.room in this.messages)) {
        this.messages[this.room] = {};
      }
      if (!(this.channel in this.messages[this.room])) {
        this.messages[this.room][this.channel] = [];
      }

      this.messages[this.room][this.channel].push(message)
      this.scrollDown()
    },

    listen() {
      const $this = this
      this.p2pt.on('peerconnect', (peer) => {
        $this.peers[peer.id] = peer
      })

      this.p2pt.on('peerclose', (peer) => {
        delete $this.peers[peer.id]
        delete $this.members[peer.id]
      })

      this.p2pt.on('msg', (peer, msg) => {
        msg = JSON.parse(msg)

        switch (msg.type) {
          case "msg-plaintext":
            console.log(msg)
            if (!(this.room in this.messages)) {
              this.messages[this.room] = {};
            }
            if (!(this.channel in this.messages[this.room])) {
              this.messages[this.room][this.channel] = [];
            }

            this.messages[this.room][this.channel].push({
              timestamp: msg.timestamp,
              username: msg.username,
              message: msg.message
            })
            this.scrollDown();
            break;
          case "msg-typing-start":
            this.usersTyping.push(msg.username)
            break;
          case "msg-typing-stop":
            this.usersTyping = this.usersTyping.filter(e => e !== msg.username)
            break;

          default:
            break;
        }

        $this.members[peer.id] = msg.username

      })

      this.p2pt.on('trackerwarning', (error, stats) => {
        console.log(error)
        if (!window.retries) window.retries = 0;
        window.retries++;
        if (window.retries >= stats.total && !trackerConnected && !warningMsg) {
          alert('We couldn\'t connect to any WebTorrent trackers. Your ISP might be blocking them 🤔');
        }
      })
      this.p2pt.start()
    },

    scrollDown() {
      this.$nextTick(() => {
        var elem = this.$refs.chatWrapper
        elem.scrollTop = elem.clientHeight + elem.scrollHeight
      })
    }
  }
}
/*
message protocol:
msg-plaintext - plaintext message with channel and server id
msg-typing - shows that a user is typing
msg-mm - file multimedia
USEME https://github.com/subins2000/simple-peer-files

srv-rq-topology - get channel topology of server(THIS IS DATED W/OLD NAMES TOO AND PRIMNAME SO WE DONT GET OVERLAPS)
srv-rs-topology - send new channel topology of server
srv-leave-server - leave a server

srv-rq-backlog - gets all messages in channel on server between dates
srv-rs-backlog - list of messages between dates in fields from and to TODO: request more peers via this.p2pt.requestMorePeers();



rtc-offer - peerless rtc offer, even if it falls on deaf ears
rtc-add - add rtc user to call
rtc-retract - remove rtc token from user that left
USEME https://github.com/feross/simple-peer#usage

*/
</script>