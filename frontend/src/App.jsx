import { useState, useEffect  } from 'react'
import './App.css'

function App() {
  const [loading, setLoading] = useState(false)
  const [message,setMessages] = useState([])
  const [report, setReport] = useState("")
  const [mediumDevice, setMediumDevice] = useState(false)
  const [clientId, setClientID] = useState('')
  const [downloadReady, setDownloadReady] = useState(false)

  useEffect(() => {
    window.addEventListener('resize', ()=>{
      if(window.outerWidth < 600){
        setMediumDevice(true)
      }else{
        setMediumDevice(false)
      }
    })

    if(window.outerWidth < 600){
      setMediumDevice(true)
    }else{
      setMediumDevice(false)
    }

    const clientId = crypto.randomUUID()
    setClientID(clientId)
    // var url = `wss://marks-pi.com/ai-researcher/ws?client_id=${clientId}`
    var url = `ws://localhost:8085/ai-researcher/ws?client_id=${clientId}`
    const ws = new WebSocket(url);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.hasOwnProperty('ping') && data.ping) return;
        if (data.hasOwnProperty("message")) {
            setMessages(prev => [...prev, data.message]);
        }
        
    };

    ws.onerror = (error) => console.error(error);
    ws.onclose = (event) => {
      console.log('webSocket closed:',event.code,event.reason)
    }

    return () => ws.close(); 
  }, []);

  async function query(){
    try{
      setLoading(true)

      var question = document.getElementById('question').value
      
      // const url = 'https://marks-pi.com/ai-researcher/ask'
      const url = 'http://localhost:8085/ai-researcher/ask'

      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({"question":question, "clientID": clientId}), 
      });

    
      var res = await response.json()
      if(res.report.length > 10){
        setDownloadReady(true)
      }
      setReport(res.report)
      setLoading(false)

    } catch(error){
      setLoading(false)
    }
    
  }

  async function downloadFile(format){
    var fn = document.getElementById('question').value.replace(/[^a-zA-Z0-9]/g, '_')
    fn = fn.replace(" ",'_')
    var url = `http://localhost:8085/ai-researcher/file?format=${format}&clientID=${clientId}&filename=${fn}`
    // var url = `https://marks-pi.com/ai-researcher/file?format=${format}&clientID=${clientId}&filename=${fn}`

    const response = await fetch(url, {
      method: "GET"
    });

    const blob = await response.blob();

    if(blob != null && blob != undefined){
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fn+'.'+format;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      return
    }

  }

  useEffect(() => {
    const textarea = document.getElementById('processingTextArea');
    textarea.scrollTop = textarea.scrollHeight;

  }, [message]); // runs whenever content changes

  return (
     <div style={{ minWidth: '98vw'}}>
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
          <div style={{display: 'flex', flexDirection:'row', justifyContent: 'space-evenly', minWidth: '90vw', minHeight:'25vh', margin:'10px 0'}}>
            <div style={{ minWidth: '40%'}}>
              <h2>Ask your question</h2>
              <textarea className='createBorder' wrap='on' style={{resize: 'none', minWidth: '100%', minHeight:'70%', fontSize:'20px', borderRadius: '10px', padding:'10px'}} id='question'></textarea>
            </div>
            <div style={{ minWidth: '40%'}}>
              <h2>Processing steps</h2>
              <textarea id='processingTextArea' className='createBorder' wrap='on' style={{resize: 'none', minWidth: '100%', minHeight: '70%', borderRadius: '10px', padding:'10px'}} readOnly='True' value={message.join('\n')}></textarea>
            </div>
          </div>
          <div style={{display: 'flex', flexDirection: 'row', minWidth:'18%', justifyContent: 'space-evenly', margin:'10px 0'}}>
            <button id='ask' disabled={loading} style={{fontSize: '20px'}} onClick={() => query()}>Ask</button>
            <button id='clear' disabled={loading} style={{fontSize: '20px'}} onClick={() => {setReport(""), setMessages([])}}>Clear Report</button>
          </div>
          <div style={{display:'flex',flexDirection:'row',justifyContent:'flex-end', maxWidth:'95vw', margin:'15px 0'}}>
            <p style={{marginRight: '10px'}}>Download Report Formats:</p>
            <button id='PDFbutton' disabled={!downloadReady} onClick={() => downloadFile('pdf')} style={{marginRight: '10px'}}>PDF</button>
            <button id='TXTbutton' disabled={!downloadReady} onClick={() => downloadFile('txt')} style={{marginRight: '10px'}}>TXT</button>
            <button id='DOCXbutton' disabled={!downloadReady} onClick={() => downloadFile('docx')} style={{marginRight: '10px'}}>DOCX</button>
          </div>
          <h2>Report</h2>
          <textarea className='createBorder' id='reportArea' wrap='on' style={{minWidth: '90vw', minHeight: '90vh', marginTop: '10px', maxWidth:'90vw', overflowX: 'auto', overflowY: 'scroll', fontSize: '20px', borderRadius: '10px', padding:'10px'}} readOnly='True' value={report}></textarea>

        </>
        : // mobile
        <>
          <div style={{display: 'flex', flexDirection:'column', justifyContent: 'space-evenly', minWidth: '90vw', minHeight:'25vh', margin:'10px 0'}}>
            <div style={{ minWidth: '40%'}}>
              <h2>Ask your question</h2>
              <textarea className='createBorder' wrap='on' style={{resize: 'none', minWidth: '90%', minHeight:'15vh', fontSize:'14px',borderRadius: '10px', padding:'10px'}} id='question'></textarea>
            </div>
            <div style={{display: 'flex', flexDirection: 'row', minWidth:'18%', justifyContent: 'space-evenly', margin:'10px 0'}}>
              <button id='ask' disabled={loading} style={{fontSize: '20px'}} onClick={() => query()}>Ask</button>
              <button id='clear' disabled={loading} style={{fontSize: '20px'}} onClick={() => {setReport(""), setMessages([])}}>Clear Report</button>
            </div>
            <div style={{ minWidth: '40%'}}>
              <h2>Processing steps</h2>
              <textarea id='processingTextArea' className='createBorder' wrap='off' style={{resize: 'none', minWidth: '90%', minHeight: '15vh', fontSize:'12px', borderRadius: '10px', padding:'10px'}} readOnly='True' value={message.join('\n')}></textarea>
            </div>
          </div>
          <div style={{display:'flex',flexDirection:'row',justifyContent:'flex-end', maxWidth:'95vw', margin:'15px 0'}}>
            <p style={{marginRight: '10px'}}>Download Report Formats:</p>
            <button id='PDFbutton' disabled={!downloadReady} onClick={() => downloadFile('pdf')} style={{marginRight: '10px'}}>PDF</button>
            <button id='TXTbutton' disabled={!downloadReady} onClick={() => downloadFile('txt')} style={{marginRight: '10px'}}>TXT</button>
            <button id='DOCXbutton' disabled={!downloadReady} onClick={() => downloadFile('docx')} style={{marginRight: '10px'}}>DOCX</button>
          </div>
          <h2>Report</h2>
          <textarea className='createBorder' id='reportArea' wrap='on' style={{minWidth: '90vw', minHeight: '90vh', marginTop: '5px', maxWidth:'90vw', overflowX: 'auto', overflowY: 'scroll', fontSize: '12px', borderRadius: '10px', padding:'10px'}} readOnly='True' value={report}></textarea>

        </>
      }
    </div>
  )
}

export default App
