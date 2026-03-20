import { useState, useEffect  } from 'react'
import './App.css'

function App() {
  const [question,setQuestion] = useState("")
  const [answer,setAnswer] = useState("")
  const [message,setMessages] = useState("")

  async function query(){
     const response = await fetch("https://marks-pi.com/ai-researcher/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({"question":question}), 
    });
    var res = await response.json()
    setAnswer(res.answer)
  }

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8085/ws");

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.hasOwnProperty("message")) {
            setMessages(prev => [...prev, data.message]);
        }
    };

    ws.onerror = (error) => console.error(error);

    return () => ws.close(); // cleanup on unmount
}, []);

  return (
     <div style={{ minWidth: '100vw'}}>
      <div>
        <h1>Logs</h1>
      </div> 
      <div style={{display:'flex', flexDirection: 'row', justifyItems: 'flex-start'}}>
        <select id='app' style={{marginLeft: '5px'}}>
          <option value='Portfolio'>Portfolio</option>
          <option value='LightsFinance'>Lights Finance</option>
          <option value='Rag'>Rag</option>
          <option value='CompressPDF'>Compress PDF</option>
          <option value='HomePage'>Home Page</option>
        </select>
        <select id='timeFrame' style={{marginLeft: '10px'}}>
          <option value='yesterday'>1 Day Ago</option>
          <option value='3 days ago'>3 Day Ago</option>
          <option value='5 days ago'>5 Day Ago</option>
          <option value='1 week ago'>1 Weeks Ago</option>
          <option value='2 weeks ago'>2 Weeks Ago</option>
        </select>
        <button style={{marginLeft: '10px'}} onClick={() => {fetchLogs()}}>View</button>
        <button onClick={() => {setLogs("Search Logs")}}>Clear logs</button>
      </div>
      <textarea wrap='off' style={{minWidth: '90vw', minHeight: '90vh', marginTop: '20px', overflowX: 'auto'}} readOnly='True' value={logs}></textarea>
    </div>
  )
}

export default App
