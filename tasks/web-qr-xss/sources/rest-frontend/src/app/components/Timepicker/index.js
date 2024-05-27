import moment from 'moment';

var firstDate = moment();
var lastDate = moment();


export  function init() {
  var html = '';
for(var i=0; i < 30; i++){
    var day = lastDate.add((i==0)? 0 : 1, 'd');
      html += '<div '+ ((i==0) ? 'class="active"' : ''  )+'><font>' + (day.date()) + '</font><br/>' + day.format('MMM') + '</div>';
    }


  SetHour(firstDate.hour());
  SetMinute(firstDate.minute());
  try {
    var tp = ((firstDate.hour())*48) ;
    document.querySelectorAll('.hour')[0].scrollTop = tp;
    var tp = ((firstDate.minute()-3)*48) ;
    document.querySelectorAll('.minute')[0].scrollTop = tp;
  }
  catch {
    console.log('closed')
  }
 
}

function SetHour(hr) {
 
  setIfPresent(document.querySelectorAll('.hour li')[3], 'active');
  setIfPresent(document.querySelectorAll('.hour li')[hr+3], 'fade');
  setIfPresent(document.querySelectorAll('.hour li')[hr+1], 'fade');
  setIfPresent(document.querySelectorAll('.hour li')[hr+4], 'fader');
  setIfPresent(document.querySelectorAll('.hour li')[hr], 'fader');
  
}

function SetFormat(fm) {
 
    setIfPresent(document.querySelectorAll('.AM_PM li')[fm+2], 'active');
    setIfPresent(document.querySelectorAll('.AM_PM li')[fm+3], 'fade');
    setIfPresent(document.querySelectorAll('.AM_PM li')[fm+1], 'fade');
    setIfPresent(document.querySelectorAll('.AM_PM li')[fm+4], 'fader');
    setIfPresent(document.querySelectorAll('.AM_PM li')[fm], 'fader');
    
  }

function SetMinute(mn) {
  
  setIfPresent(document.querySelectorAll('.minute li')[mn+3], 'active');
  setIfPresent(document.querySelectorAll('.minute li')[mn+3], 'fade');
  setIfPresent(document.querySelectorAll('.minute li')[mn+1], 'fade');
  setIfPresent(document.querySelectorAll('.minute li')[mn-4], 'fader');
  setIfPresent(document.querySelectorAll('.minute li')[mn], 'fader');

}

function moveDate(scr) {
  var lft = scr.scrollLeft;
  var ind = Math.floor((lft + 40) / 80);
  var d = document.getElementById('DP-date');
  document.querySelectorAll('.swipe-wrap div.active')[0].className = '';
  d = d.getElementsByTagName('div');
  d[ind].className = 'active';
}

export function moveHour(hr) {
 
  var tp = hr.scrollTop;
  var ind = Math.floor((tp + 24) / 48) + 2;
  
   var d = document.querySelectorAll('.hour li');
   setIfPresent(document.querySelectorAll('.hour li.active')[0], '');
   setIfPresent(document.querySelectorAll('.hour li.fade')[0], '');
   setIfPresent(document.querySelectorAll('.hour li.fade')[0], '');
   setIfPresent(document.querySelectorAll('.hour li.fader')[0], '');
   setIfPresent(document.querySelectorAll('.hour li.fader')[0], '');
  
   setIfPresent(d[ind], 'active');
   setIfPresent(d[ind-1], 'fade');
   setIfPresent(d[ind+1], 'fade');
   setIfPresent(d[ind-1], 'fader');
   setIfPresent(d[ind+2], 'fader');
   try {
    if (scrollTimer != -1)
      clearTimeout(scrollTimer);
   scrollTimer = window.setTimeout(function(){
      document.querySelectorAll('.hour')[0].scrollTop = (ind-2)*48;
   }, 200);
   }
   catch {
    console.log('closed')
   }
   


}

export function moveFormat(fm) {
    
    var tp = fm.scrollTop;
    var ind = Math.floor((tp + 24) / 48) + 2;
    
     var d = document.querySelectorAll('.AM_PM li');
     
     setIfPresent(document.querySelectorAll('.AM_PM li.active')[0], '');
     setIfPresent(document.querySelectorAll('.AM_PM li.fade')[0], '');
     setIfPresent(document.querySelectorAll('.AM_PM li.fade')[0], '');
     setIfPresent(document.querySelectorAll('.AM_PM li.fader')[0], '');
     setIfPresent(document.querySelectorAll('.AM_PM li.fader')[0], '');
    
     setIfPresent(d[ind-2], 'active');
     setIfPresent(d[ind-1], 'fade');
     setIfPresent(d[ind+1], 'fade');
     setIfPresent(d[ind-1], 'fader');
     setIfPresent(d[ind+2], 'fader');
     try {
        if (scrollTimer != -1)
          clearTimeout(scrollTimer);
       scrollTimer = window.setTimeout(function(){
          document.querySelectorAll('.AM_PM')[0].scrollTop = (ind-2)*48;
       }, 200);
       }
       catch {
        console.log('closed')
       }
       
  
  }


  var scrollTimer = -1;
 export function moveMinute(mn) {
   var tp = mn.scrollTop;
   var ind = Math.floor((tp + 24) / 48) + 2;
  
   var d = document.querySelectorAll('.minute li');

   setIfPresent(document.querySelectorAll('.minute li.active')[0], '');
   setIfPresent(document.querySelectorAll('.minute li.fade')[0], '');
   setIfPresent(document.querySelectorAll('.minute li.fade')[0], '');
   setIfPresent(document.querySelectorAll('.minute li.fader')[0], '');
   setIfPresent(document.querySelectorAll('.minute li.fader')[0], '');
  
   setIfPresent(d[ind], 'active');
   setIfPresent(d[ind-1], 'fade');
   setIfPresent(d[ind+1], 'fade');
   setIfPresent(d[ind-1], 'fader');
   setIfPresent(d[ind+2], 'fader');
   try {
    if (scrollTimer != -1)
      clearTimeout(scrollTimer);
   scrollTimer = window.setTimeout(function(){
      document.querySelectorAll('.minute')[0].scrollTop = (ind-2)*48;
   }, 200);
   }
   catch {
    console.log('closed')
   }
   

 }

 function setIfPresent(elem, cls) {
  if(typeof elem !== 'undefined') {
    elem.className = cls;
  }
}