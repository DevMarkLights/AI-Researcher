import { useState, useEffect  } from 'react'
import './App.css'

function App() {
  const [loading, setLoading] = useState(false)
  const [message,setMessages] = useState([])
  const [report, setReport] = useState("")
  const [mediumDevice, setMediumDevice] = useState(false)
  const [fontSize, setFontSize] = useState('12px')

  async function query(){
    try{
      setLoading(true)

      var question = document.getElementById('question').value
      const url = 'http://localhost:8085/ask'
      // const url = "https://marks-pi.com/ai-researcher/ask"
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({"question":question}), 
      });

    
      var res = await response.json()
      setReport(res.report)
      setLoading(false)

    } catch(error){
      setLoading(false)
    }
    
  }


  useEffect(() => {
    window.addEventListener('resize', ()=>{
      if(window.outerWidth < 600){
        setMediumDevice(true)
        setFontSize('12px')
      }else{
        setMediumDevice(false)
        setFontSize('20px')
      }
    })

    if(window.outerWidth < 600){
      setMediumDevice(true)
      setFontSize('12px')
    }else{
      setMediumDevice(false)
      setFontSize('20px')
    }
    const ws = new WebSocket("ws://localhost:8085/ws");

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.hasOwnProperty("message")) {
            setMessages(prev => [...prev, data.message]);
        }
    };

    ws.onerror = (error) => console.error(error);

    return () => ws.close(); 
}, []);

  return (
     <div style={{ minWidth: '100vw'}}>
      <div>
        <h1>AI Researcher</h1>
      </div> 
      {
        loading &&
        <div className="loader"></div>

      }
      {
        !mediumDevice ?
        <>
          <div style={{display: 'flex', flexDirection:'row', justifyContent: 'space-evenly', minWidth: '100vw', minHeight:'25vh', margin:'10px 0'}}>
            <div style={{ minWidth: '40%'}}>
              <h2>Ask your question</h2>
              <textarea className='createBorder' wrap='on' style={{resize: 'none', minWidth: '100%', minHeight:'80%', fontSize:'20px'}} id='question'></textarea>
            </div>
            <div style={{ minWidth: '40%'}}>
              <h2>Processing steps</h2>
              <textarea className='createBorder' wrap='on' style={{resize: 'none', minWidth: '100%', minHeight: '80%'}} id='processing steps' readOnly='True' value={message.join('\n')}></textarea>
            </div>
          </div>
          <div style={{display: 'flex', flexDirection: 'row', minWidth:'18%', justifyContent: 'space-evenly'}}>
            <button id='ask' disabled={loading} style={{fontSize: '20px'}} onClick={() => query()}>Ask</button>
            <button id='clear' disabled={loading} style={{fontSize: '20px'}} onClick={() => {setReport(""), setMessages([])}}>Clear Report</button>
          </div>
          <textarea className='createBorder' id='reportArea' wrap='on' style={{minWidth: '90vw', minHeight: '90vh', marginTop: '20px', maxWidth:'90vw', overflowX: 'auto', overflowY: 'scroll', fontSize: '20px'}} readOnly='True' value={report}></textarea>

        </>
        :
        <>
          <div style={{display: 'flex', flexDirection:'column', justifyContent: 'space-evenly', minWidth: '90vw', minHeight:'25vh', margin:'10px 0'}}>
            <div style={{ minWidth: '40%'}}>
              <h2>Ask your question</h2>
              <textarea className='createBorder' wrap='on' style={{resize: 'none', minWidth: '90%', minHeight:'15vh', fontSize:'14px'}} id='question'></textarea>
            </div>
            <div style={{display: 'flex', flexDirection: 'row', minWidth:'18%', justifyContent: 'space-evenly', margin:'10px 0'}}>
              <button id='ask' disabled={loading} style={{fontSize: '20px'}} onClick={() => query()}>Ask</button>
              <button id='clear' disabled={loading} style={{fontSize: '20px'}} onClick={() => {setReport(""), setMessages("")}}>Clear Report</button>
            </div>
            <div style={{ minWidth: '40%'}}>
              <h2>Processing steps</h2>
              <textarea className='createBorder' wrap='off' style={{resize: 'none', minWidth: '90%', minHeight: '15vh', fontSize:'12px'}} id='processing steps' readOnly='True' value={message.join('\n')}></textarea>
            </div>
          </div>
          <textarea className='createBorder' id='reportArea' wrap='on' style={{minWidth: '90vw', minHeight: '90vh', marginTop: '20px', maxWidth:'90vw', overflowX: 'auto', overflowY: 'scroll', fontSize: '12px'}} readOnly='True' value={report}></textarea>

        </>
      }
    </div>
  )
}

export default App
