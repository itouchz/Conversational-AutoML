import React from 'react'
import axios from 'axios'
import './App.css';

class App extends React.Component {
  state = {
    status: 'standby',
    currentUserMessage: '',
    botState: 0,
    botResponse: null,
    requiredInfo: { task: null, method: null, data_source: null, data_type: null, dataset: null, target: null, delivery: null },
    messages: [],
    showUploadBox: false,
    showFirstExample: false,
    userFile: null,
    isDelivered: false,
    isStarted: false,
    currentModel: null,
    predictedResult: '',
    currentInputText: '',
    imageFile: null
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
      requiredInfo: { task: null, method: null, data_source: null, data_type: null, dataset: null, target: null, delivery: null },
      messages: [],
      showUploadBox: false,
      showFirstExample: false,
      userFile: null,
      isDelivered: false,
      isStarted: false,
      currentModel: null,
      predictedResult: '',
      currentInputText: '',
      imageFile: null
    })
    this.setState({ messages: [data] })
  }

  getBotMessage = async () => {
    let { data } = await axios.get('http://localhost:5000/greet')
    this.setState({ messages: [data] })
  }

  getSlotRequestMessage = empty_slots => {
    let length = empty_slots.length
    let message = { sender: 'Bot', text: '' }
    let key = length > 0 ? empty_slots[0] : ''
    let idx = Math.floor(Math.random() * 3)
    let { task, method, data_source, data_type, dataset, delivery } = this.state.requiredInfo

    switch (key) {
      case 'task':
        message.text = ['Which <strong>task</strong> (classification or regression) do you want?',
          'Please specify whether you want <strong>classifier</strong> or <strong>regressor</strong>.',
          'What <strong>problem</strong> (classification or regression) you are looking for?'][idx]
        this.setState({ showUploadBox: false })
        break;
      case 'method':
        message.text = ['Which <strong>learning method</strong> (machine learning or deep learning) do you want?',
          'Please specify whether you want <strong>ML model</strong> or <strong>DL model</strong>.',
          'What <strong>learning approach</strong> (machine learning or deep neural network) you are looking for?'][idx]
        this.setState({ showUploadBox: false })
        break;
      case 'data_source':
        message.text = ['Please specify the available <a href="https://www.tensorflow.org/datasets/catalog" target="_blank">open dataset name</a> or request for an upload.',
          'What is your training data set? <br/> (enter the built-in <a href="https://www.tensorflow.org/datasets/catalog" target="_blank">public data</a> or simply type <i>upload</i> for upload your own data)',
          'Enter any <a href="https://www.tensorflow.org/datasets/catalog" target="_blank">available dataset <i>name</i></a> or <i>upload</i> if you have your own data for training!'][idx]
        this.setState({ showUploadBox: false })
        break;
      case 'data_type':
        message.text = ['Please specify your data set type (image, text, or structured data.',
          'What is your training data set type? (only image, text, and tabular data for now)',
          'Which one (text, image, or tabular data) is your training data set type?'][idx]
        this.setState({ showUploadBox: false })
        break;
      case 'dataset':
        if (this.state.requiredInfo['data_source'] === 'user_define') {
          message.text = `Please upload your data set below.`
          this.setState({ showUploadBox: true })
        }
        break;
      case 'target':
        if (this.state.requiredInfo['data_source'] === 'user_define') {
          message.text = ['Please tell me your <i>target variable</i> name.',
            'What is your target feature name?',
            'Which column <i>name</i> is your <strong>target variable</strong> that you want it to be predicted?'][idx]
        }
        this.setState({ showUploadBox: false })
        break;
      case 'delivery':
        message.text = ['How do you want to get your model (this chat or email)?',
          'Please specify the channel (chatbox or email) you want to get you model.',
          'Do you would like to get your email by this chatbox or email?'][idx]
        this.setState({ showUploadBox: false })
        break;
      default:
        if (this.state.isStarted === false) {
          message.text = `
          <strong>Task</strong>: ${task === 'cls' ? 'classification' : 'regression'} <br/>
          <strong>Learning Method</strong>: ${method === 'dl' ? 'Deep Learning' : 'Machine Learning'} <br/>
          <strong>Data Source</strong>: ${data_source === 'built_in' ? 'Public Dataset' : 'Uploaded Data'} <br/>
          <strong>Data Type</strong>: ${data_type.charAt(0).toUpperCase() + data_type.slice(1)} <br/>
          <strong>Dataset</strong>: ${dataset} <br/>
          <strong>Delivery</strong>: ${delivery === 'chat' ? 'Chatbox' : 'E-Mail'}
          `
        } else if (this.state.isStarted && this.state.isDelivered === false) {
          message.text = 'Your model is building!~'
        } else {
          message.text = "Completed!"
        }
        this.setState({ showUploadBox: false })
        break;

    }

    if (message.text === '') {
      message.text = `Sorry! I don't understand you. Please see the examples~`
    }

    return message
  }

  onFileChange = e => {
    this.setState({ userFile: this.userFile })
  }

  onImageChange = e => {
    this.setState({ imageFile: this.imageFile })
  }

  handlePredictImage = async e => {
    e.preventDefault()

    let messages = this.state.messages

    const formData = new FormData()
    formData.append('file', this.imageFile.files[0])
    formData.append('model', this.state.currentModel)
    formData.append('target', this.state.requiredInfo.target)

    this.setState({ imageFile: null })
    let { data } = await axios.post('http://localhost:7000/image/get_prediction', formData)

    messages.push({
      sender: 'User', text: `<img src="http://localhost:7000/img/${data.img_name}" width=128 height=128/>`
    })

    messages.push(data)

    this.setState({ messages })
    document.getElementsByClassName('MessageList')[0].scrollTo(0, 600)
  }

  handlePredictText = async e => {
    e.preventDefault()

    let messages = this.state.messages
    let inputText = this.state.currentInputText

    if (this.state.currentInputText !== '') {
      messages.push({ sender: 'User', text: this.state.currentInputText })
      this.setState({ messages, currentInputText: '' })

      let { data } = await axios.post('http://localhost:7000/text/get_prediction', { model: this.state.currentModel, target: this.state.requiredInfo.target, input_text: inputText })

      messages.push(data)

      this.setState({ messages })
      document.getElementsByClassName('MessageList')[0].scrollTo(0, 600)
    }
  }

  handleUploadFile = async e => {
    e.preventDefault()
    let messages = this.state.messages

    const formData = new FormData()
    formData.append('file', this.userFile.files[0])
    formData.append('current_state', this.state.status)
    formData.append('user_slot', this.state.requiredInfo)

    let { data } = await axios.post('http://localhost:5000/upload', formData)

    let slots = data.user_slot
    let { requiredInfo } = this.state
    let empty_slots = []

    for (const key of Object.keys(slots)) {
      requiredInfo[key] = slots[key]
      if (slots[key] == null) empty_slots.push(key)
    }

    data.text += this.getSlotRequestMessage(empty_slots).text
    messages.push(data)

    this.setState({ messages, status: data.current_state, showUploadBox: false })
    document.getElementsByClassName('MessageList')[0].scrollTo(0, 600)
  }

  sendUserMessage = async () => {
    let messages = this.state.messages
    let currentUserMessage = this.state.currentUserMessage
    if (this.state.currentUserMessage !== '') {
      messages.push({ sender: 'User', text: this.state.currentUserMessage })
      this.setState({ messages, currentUserMessage: '' })

      let { data } = await axios.post('http://localhost:5000/bot', { currentState: this.state.status, message: currentUserMessage })

      if (data.current_state === 'building' && this.state.isStarted) {
        let workingMessage = ["I'm working on it~", "Please wait...", "Thank you for your patience!", "The work is in progress.", "I will do my best!~"]
        messages.push({ sender: 'Bot', text: workingMessage[Math.floor(Math.random() * 5)] })
        this.setState({ messages })
      }

      if (data.current_state === 'building' && this.state.isStarted === false) {
        this.setState({ isStarted: true })

        let { data } = await axios.post('http://localhost:7000/get_model', { user_slot: this.state.requiredInfo })
        let { model, score, metric, summary } = data

        messages.push({ sender: 'Bot', text: `Your model performance is <strong>${score}</strong> in ${metric} metric.` })

        this.setState({ isDelivered: true, status: 'standby', currentModel: model })
      } else {
        let slots = data.user_slot
        let { requiredInfo } = this.state
        let empty_slots = []

        for (const key of Object.keys(slots)) {
          requiredInfo[key] = slots[key]
          if (slots[key] == null) empty_slots.push(key)
        }

        data.text += this.getSlotRequestMessage(empty_slots).text
        messages.push(data)
      }

      this.setState({ messages, status: data.current_state })
      document.getElementsByClassName('MessageList')[0].scrollTo(0, 600)
    }
  }

  render() {
    let { status, requiredInfo, currentUserMessage, messages } = this.state
    let { task, method, data_source, data_type, dataset, target, delivery } = requiredInfo
    return (
      <div className="App">
        <h1 style={{ color: 'white', marginTop: 0 }}>Conversational AutoML</h1>
        <div style={{ display: 'flex', justifyContent: 'space-between', width: 680 }}>
          <div><span style={{ color: 'white', fontWeight: 'bold' }}>Status: </span><span style={{ color: status === 'building' ? 'white' : status === 'active' ? 'lightgreen' : status === 'standby' ? 'orange' : 'black' }}>{status}</span></div>
          <button onClick={this.onReset}>Reset</button>
        </div>
        <div className="Container">
          <div style={{ fontSize: 'smaller' }}>
            <div style={{ fontWeight: 'bold' }}>Required Information: </div>
            <span className="RequireInfoBox"> Task: {task ? '✔️' : '❌'} </span>
            <span className="RequireInfoBox"> Method: {method ? '✔️' : '❌'} </span>
            <span className="RequireInfoBox"> Data Source: {data_source ? '✔️' : '❌'}</span>
            <span className="RequireInfoBox"> Data Type: {data_type ? '✔️' : '❌'}</span>
            <span className="RequireInfoBox"> Data Set: {dataset ? '✔️' : '❌'}</span>
            <span className="RequireInfoBox"> Target Variable: {target ? '✔️' : '❌'}</span>
            <span className="RequireInfoBox"> Delivery: {delivery ? '✔️' : '❌'}</span>
          </div>

          <hr />

          <div className="MessageList">
            {
              messages.map((message, index) => (
                <div key={index} className={`MessageItem ${message.sender}`}>
                  {message.sender === 'Bot' ? <div className="SenderAvatar"><img src="https://www.flaticon.com/svg/static/icons/svg/3398/3398634.svg" alt="Converstaion AutoML Bot" width={48} /></div> : null}
                  <div className="MessageContentBox"> <div dangerouslySetInnerHTML={{ __html: message.text }} /></div>
                </div>
              ))
            }
          </div>

          {
            this.state.showUploadBox ?
              <form onSubmit={this.handleUploadFile}>
                <input type="file" name="file" ref={ref => { this.userFile = ref }} onChange={this.onFileChange} accept=".csv" />
                <button className="upload-btn" disabled={!this.state.userFile}>Upload</button>
              </form> : null
          }

          {
            this.state.isDelivered ?
              <div>Download you model <a href={`http://localhost:7000/download/${this.state.currentModel}.zip`}>here</a>
                {
                  data_type === 'text' ? <div>
                    <input style={{ width: 670 }} value={this.state.currentInputText} onChange={event => this.setState({ currentInputText: event.target.value })} type="text" name="input-text" />
                    <button onClick={this.handlePredictText} className="upload-btn" disabled={!this.state.currentInputText}>Predict</button>
                  </div> : data_type === 'image' ? <div>
                    <form onSubmit={this.handlePredictImage}>
                      <input type="file" name="file-image" ref={ref => { this.imageFile = ref }} onChange={this.onImageChange} accept=".png, .jpg, .jpeg" />
                      <button className="upload-btn" disabled={!this.state.imageFile}>Predict</button>
                    </form>
                  </div> : null
                }
              </div> : null
          }

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
