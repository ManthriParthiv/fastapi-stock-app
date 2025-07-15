import { Routes, BrowserRouter,Route } from "react-router-dom";
import Home from './components/Home'
import AnalysedStocks from './components/AnalysedStocks'
import Stocks from './components/Stocks'
const App=()=>{
  return(
    <BrowserRouter>
    <Routes>
  <Route path="/" element={<Home/>}/>
<Route path="/stocks" element={<Stocks/>}/>
<Route path="/analysed-stocks" element={<AnalysedStocks/>}/>
    </Routes>
    </BrowserRouter>
    
  )
}
export default App;