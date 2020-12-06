import React from 'react'
import axios from 'axios'
import './App.css';

class App extends React.Component {
  state = {
    status: 'standby',
    currentUserMessage: '',
    botState: 0,
    botResponse: null,
    requiredInfo: { task: null, dataSource: null, dataset: null, targetVariable: null, delivery: null },
    messages: []
  }

  componentDidMount() {
    this.getBotMessage()
  }

  onReset = async () => {
    let { data } = await axios.get('http://localhost:5000/reset')
    this.setState({
      status: 'standby',
      currentUserMessage: '',
      botState: 0,
      botResponse: null,
      requiredInfo: { task: null, dataSource: null, dataset: null, targetVariable: null, delivery: null },
      messages: [],
      showFirstExample: false
    })
    this.setState({ messages: [data] })
  }

  getBotMessage = async () => {
    let { data } = await axios.get('http://localhost:5000/greet')
    this.setState({ messages: [data] })
  }

  getSlotRequestMessage = () => {

  }

  sendUserMessage = async () => {
    let messages = this.state.messages
    if (this.state.currentUserMessage !== '') {
      messages.push({ sender: 'User', text: this.state.currentUserMessage })
      this.setState({ messages, currentUserMessage: '' })

      let { data } = await axios.post('http://localhost:5000/bot', { currentState: this.state.status, message: this.state.currentUserMessage })

      messages.push(data)

      let slots = data.user_slot
      let { requiredInfo } = this.state
      for (const key of Object.keys(slots)) {
        if (key === 'task') {
          requiredInfo.task = slots[key]
        }
      }

      this.setState({ messages, status: data.current_state })
    }
  }

  render() {
    let { status, requiredInfo, currentUserMessage, messages } = this.state
    let { task, dataSource, dataset, targetVariable, delivery } = requiredInfo
    return (
      <div className="App">
        <h1 style={{ color: 'white', marginTop: 0 }}>Conversational AutoML</h1>
        <div style={{ display: 'flex', justifyContent: 'space-between', width: 680 }}>
          <div><span style={{ color: 'white', fontWeight: 'bold' }}>Status: </span><span style={{ color: status === 'Active' ? 'lightgreen' : 'black' }}>{status}</span></div>
          <button onClick={this.onReset}>Reset</button>
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
