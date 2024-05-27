import React, {useState} from 'react'
import Calendar from 'react-calendar'
import 'react-calendar/dist/Calendar.css';
import styles from './datepicker.css'
import { Inter } from 'next/font/google';

const inter = Inter({subsets: ['latin']})

export default function Datepicker({showCalendar, setShowCalendar, setTimePicker, setDateExt}) {
  const [date, setDate] = useState(new Date())
  const [label, setLabel] = useState(new Date)
  
  let onChange = (e) => {
    setDate(e)
    setDateExt(date)
  }
 
  return (
    <>

      <button onClick={() => {setShowCalendar(!showCalendar); setTimePicker(false)}} className='w-full bg-orange-primary  h-[56px] rounded-[20px] text-bg-white-styled text-[18px] active:bg-orange-primary '>{date.toLocaleString("en-US", { month: "long", day: '2-digit' })}</button>
      {showCalendar && <Calendar 
      className={inter.className}
      value={date}
      onChange={onChange}
      locale='en-US'
      minDetail='month'
      next2Label={null} 
      prev2Label={null}
      navigationLabel={({ date, label, locale, view }) => (`${date.toLocaleDateString(locale, {month: 'short'})}`)}
      showNeighboringMonth={false}
      onClickDay={() => setShowCalendar(false)}
      />}
   
    </>
  )
}

