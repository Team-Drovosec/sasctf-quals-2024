'use client'
import useLongPress from "./useLongPress";
import { Aldrich } from "next/font/google";
import Image from "next/image";
import { useState } from "react";

import img_kiss from "./images/kiss.gif";
import img_back_arrow from "./images/back_arrow.png"
import img_doctor_w from "./images/doctor_WOMAN_2.jpg"
import img_doctor from "./images/doctor.jpg"
import img_download_arrow from "./images/download_arrow.png"
import img_tongue from "./images/tongue.png"

const aldrich = Aldrich({ subsets: ['latin'], weight: '400' })



export default function Home() {
  const [loading, setLoading] = useState(false)
  const [cat, setCat] = useState(false)
  const [form, setForm] = useState(false)
  const [resultLoading, setResultLoading] = useState(false)
  const [result, setResult] = useState(false)
  const [error, setError] = useState('')
  const [name, setName] = useState('')
  const [birth, setBirth] = useState('')
  const [id, setId] = useState('')
  const [qr_image, setQR] = useState('')

  const defaultOptions = {
    shouldPreventDefault: true,
    delay: 3000,
  };
  const onLongPress = () => {
    setCat(true)
    setLoading(false)
    setTimeout(setCat, 2250, false)
    setTimeout(setForm, 2260, true)
  };

  const onClick = () => {
  }
  const isInputsValid = () => {
    return name.match('^[^\\x00-\\x1F<>\"\'();]{3,55}$') && birth.match('^[12][0-9]{3}-[01][0-9]-[0-3][0-9]$') && parseInt(id).toString() === id && 1000000 < parseInt(id) && parseInt(id) < 999999999
  }
  const longPressEvent = useLongPress(onLongPress, onClick, setLoading, defaultOptions);

  const continueHandler = () => {
    setResultLoading(true)
    fetch('/get_qr', {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: `birth_date=${birth}&fullname=${name}&id_number=${id}`
    }).then(res => {
      if (res.headers.get('Content-Type') != 'image/png'){
        setTimeout(setError, 2000, '')
        setResultLoading(false)
        return setError('Server Error!')
      }
      res.blob().then(blob => {
        setQR(blob)
        setResult(true)
        setResultLoading(false)
      })
    }).catch(err => {
      setTimeout(setError, 2000, '')
      setResultLoading(false)
      setError('Server Error!')
    })
  }

  if (global?.window && (window.navigator.userAgentData.mobile === false || window.innerHeight < window.innerWidth)) {
    return (<> <main className="flex min-h-screen flex-col items-center justify-center"> <p className="p-5 m-0 text-5"> Please use your mobile device to run this service! </p> </main> </>)
  }

  return (
    <>
   
    <main className="flex min-h-screen flex-col items-center  justify-center " >
    <Image  priority={true} src={img_kiss} alt="kiss" className="rounded-[20px] w-full h-[350px] hidden" width={350} height={350} />
      <div className="flex flex-col items-center justify-start max-w-screen-sm w-full ">
        <div className="pt-5 pl-5 pb-1 flex w-full border-liquid-accent border-solid border-b-2 min-w-[350px]">
          <h1 className={`${aldrich.className} text-liquid-primary self-start text-3xl`}>LiquidLab</h1>
        </div>

        {!form && <div className="w-full max-w-screen-md">
          <Image src={img_doctor} className="max-w-screen-sm w-full" width={350} height={250} alt="doctor" />
          <div className="px-5 flex justify-center">
            <div className="px-5 top-[35%] rounded-[20px] rounded-br-[60px] absolute text-bg-white bg-liquid-accent w-full min-w-[350px] max-w-screen-sm">
              <p className="p-5 m-0 text-5 ">Welcome to the PCRMobile™ by LiquidLab. Put your tongue in the organic material collection zone to proceed.</p>
            </div>

            {loading && <div >
              <div className=" w-full" role="status">
                <svg aria-hidden="true" className=" left-0 right-0 top-[40%] ml-auto mr-auto absolute w-20 h-20 text-liquid-text animate-spin dark:text-liquid-text fill-liquid-accent" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor" />
                  <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill" />
                </svg>
                <span className="sr-only">Loading...</span>
              </div>
            </div>}

          </div>

          


          <div  className="px-5 pt-14 mb-4 w-full cursor-pointer justify-center h-full ">
          <div className="pb-8 flex justify-center items-center gap-2 text-5">
            <span>Please, keep your tongue in the zone for 3 seconds...</span>
            <svg style={{ color: 'rgb(20, 197, 187)' }} xmlns="http://www.w3.org/2000/svg"  fill="currentColor" className=" animate-bounce w-5 bi bi-arrow-down-circle" viewBox="0 0 16 16"> <path fillRule="evenodd" d="M1 8a7 7 0 1 0 14 0A7 7 0 0 0 1 8zm15 0A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.5 4.5a.5.5 0 0 0-1 0v5.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V4.5z" fill="#14c5bb"></path> </svg>
          </div>
            <div {...longPressEvent} style={{'background': 'url(' + img_tongue.src + ')', 'background-repeat': 'no-repeat', 'background-position': 'center', 'background-size': 'contain'}} className="bg-no-repeat h-full bg-center bg-contain w-full min-h-[350px] mb-8">
            </div>
          </div>


        </div>}

        {form && !resultLoading && !result && !error && <div className="w-full animate-slideLeft h-screen min-w-[350px] pt-8 left-0">

          <div className="px-5 flex flex-col justify-center items-start gap-[24px] mb-[35px] w-full">
            <Image onClick={() => setForm(false)} src={img_back_arrow} className="cursor-pointer" alt="arrow" width={45} height={2} />

            <div className="flex flex-col gap-4 w-full" >
              <h3 className="text-lg">Full name</h3>
              <input onChange={(e) => setName(e.target.value)} type="text" placeholder="Firstname Lastname" className="w-full drop-shadow-md focus:outline-none bg-bg-white h-[60px] pl-4 text-liquid-accent rounded-xl" />
            </div>

            <div className="flex flex-col gap-4 w-full" >
              <h3 className="text-lg">Date of Birth</h3>
              <input onChange={(e) => setBirth(e.target.value)} type="text" placeholder="0000-00-00" className="w-full focus:outline-none placeholder:text-liquid-accent drop-shadow-md pl-4 text-liquid-accent bg-bg-white h-[60px] rounded-md" />
            </div>

            <div className="flex flex-col gap-4 w-full" >
              <h3 className="text-lg">ID Number</h3>
              <input  onChange={(e) => setId(e.target.value)}type="phone" placeholder="1000000" className="w-full drop-shadow-md focus:outline-none  bg-bg-white h-[60px] pl-4 text-liquid-accent rounded-xl" />
            </div>
            
            <button disabled={(isInputsValid()) ? false : true } onClick={continueHandler} className="w-full bg-liquid-accent rounded-xl text-bg-white py-[16px] text-xl active:bg-[#12AEA5] disabled:opacity-[0.5] ">Continue</button>
            

          </div>

        </div>}

        {resultLoading && <div>
          <div className="w-full h-screen pt-[250px]" role="status">
            <svg aria-hidden="true" className="w-20 h-20 text-liquid-text animate-spin dark:text-liquid-text fill-liquid-accent" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor" />
              <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill" />
            </svg>
            <span className="sr-only">Loading...</span>
          </div>
        </div>}

        {error && <div>
          <div className="w-full h-screen pt-[250px]" role="status">
            <span className="justify-center items-center">{error}</span>
          </div>
        </div>}

        {result && <div className="max-w-screen-sm">
          <Image src={img_doctor_w} className="max-w-screen-sm w-full" width={350} height={250} alt="doctor" />
          <div className="px-5 flex justify-center mb-4">
            <div className=" top-[250px] rounded-[20px] rounded-br-[60px] absolute text-bg-white bg-liquid-accent  ">
              <p className="p-5 m-0 text-5 ">Show this QR code on demand</p>
            </div>



          </div>
          <div className="px-5">
            <div className="px-5 border rounded-t-3xl border-liquid-accent border-solid">
              <Image src={URL.createObjectURL(qr_image)} id="qrimg" className="border-none" width={350} height={350} />
            </div>
            <a href={URL.createObjectURL(qr_image)} download="liquidlab.png" className="px-5 py-2 cursor-pointer bg-liquid-accent flex justify-center  mb-4 border rounded-b-3xl border-liquid-accent border-solid">
              <Image src={img_download_arrow} className="border-none" width={40} height={40} />
            </a>

          </div>



        </div>}



        {cat && <div className='flex px-5  flex-col justify-end h-full items-center w-full fixed bottom-0 backdrop-blur-md bg-bg-liquid-blur right-auto  '>
          <div className="pb-12">
            <Image  priority={true} src={img_kiss} alt="kiss" className="rounded-[20px] w-full h-[350px]" width={350} height={350} />
          </div>

        </div>}

      </div>


    </main>
    </>
  );
}
