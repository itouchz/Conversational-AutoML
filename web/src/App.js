import React from 'react'
import axios from 'axios'
import './App.css';

class App extends React.Component {
  state = {
    status: 'Active',
    currentUserMessage: '',
    botState: 0,
    botResponse: null,
    requiredInfo: { task: null, dataSource: null, dataset: null, targetVariable: null, delivery: null },
    messages: []
  }

  componentDidMount() {
    this.getBotMessage()
  }

  getBotMessage = () => {
    // call API by axios
    let botMessage = "Hi! I'm your Conversational AutoML Bot~"
    let messages = this.state.messages
    messages.push({ sender: 'Bot', text: botMessage })
    this.setState({ messages })
  }

  sendUserMessage = () => {
    let messages = this.state.messages
    messages.push({ sender: 'User', text: this.state.currentUserMessage })
    // call API for getting a response for the given user message
    this.setState({ messages, currentUserMessage: '' })
  }

  render() {
    let { status, requiredInfo, botResponse, currentUserMessage, messages } = this.state
    let { task, dataSource, dataset, targetVariable, delivery } = requiredInfo
    return (
      <div className="App">
        <h1 style={{ color: 'white', marginTop: 0 }}>Conversational AutoML</h1>
        <div style={{ display: 'flex', justifyContent: 'space-between', width: 680 }}>
          <div><span style={{ color: 'white', fontWeight: 'bold' }}>Status: </span><span style={{ color: status === 'Active' ? 'lightgreen' : 'black' }}>{status}</span></div>
          <button>Reset</button>
        </div>
        <div className="Container">
          <div>
            <span style={{ fontWeight: 'bold' }}>Required Information: </span>
            <span className="RequireInfoBox"> Task: {task ? '✔️' : '❌'} </span>
            <span className="RequireInfoBox"> Data Set: {dataset ? '✔️' : '❌'}</span>
            <span className="RequireInfoBox"> Target Variable: {targetVariable ? '✔️' : '❌'}</span>
            <span className="RequireInfoBox"> Delivery: {delivery ? '✔️' : '❌'}</span>
          </div>

          <hr />

          <div className="MessageList">
            {
              messages.map((message, index) => (
                <div key={index} className={"MessageItem" + " " + message.sender}>
                  {message.sender === 'Bot' ? <div className="SenderAvatar"><img src="https://www.flaticon.com/svg/static/icons/svg/1767/1767001.svg" alt="Converstaion AutoML Bot" width={32} /></div> : null}
                  <div className="MessageContentBox">{message.text}</div>
                </div>
              ))
            }
          </div>

          <hr />

          <div className="EntryBox">
            <input value={currentUserMessage} onChange={event => this.setState({ currentUserMessage: event.target.value })} type="text" name="message" className="TextEntryBox" placeholder='Please request a model your want here! (Ex.) I want a image classification model.' />
            <button onClick={this.sendUserMessage} style={{ border: '1px solid grey', borderRadius: 0, background: 'lightgrey' }}>Send</button>
          </div>
        </div>
      </div>
    )
  }
}

export default App;
