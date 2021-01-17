function printClock() {

    var clock = document.getElementById("clock");
    var currentDate = new Date();
    var calendar = currentDate.getFullYear() + "-" + (currentDate.getMonth()+1) + "-" + currentDate.getDate()
    var amPm = 'AM';
    var currentHours = addZeros(currentDate.getHours(),2); 
    var currentMinute = addZeros(currentDate.getMinutes() ,2);
    var currentSeconds =  addZeros(currentDate.getSeconds(),2);
    
    if(currentHours >= 12){
        amPm = 'PM';
        currentHours = addZeros(currentHours - 12,2);
    }

    if(currentSeconds >= 50){
        currentSeconds = '<span style="color:#de1951;">'+currentSeconds+'</span>'
    }
    clock.innerHTML = currentHours+":"+currentMinute+":"+currentSeconds +" <span style='font-size:50px;'>"+ amPm+"</span>";
    
    setTimeout("printClock()",1000);
}

function addZeros(num, digit) {
        var zero = '';
        num = num.toString();
        if (num.length < digit) {
        for (i = 0; i < digit - num.length; i++) {
            zero += '0';
        }
        }
        return zero + num;
}    