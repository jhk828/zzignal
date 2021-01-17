function update_weather() {

	req = $.ajax({
		url : '/update_weather',
		type : 'POST',
		data : {}
	});

	req.done(function(data) {

		var desc = data.currentWeather.desc;
		var icon = data.currentWeather.icon;
		var temperature = data.currentWeather.temperature;
		var title = data.currentWeather.title;
		var week = data.currentWeather.week_summary;

		var time0 = data.currentWeather.time0;
		var time0_hightemp = data.currentWeather.time0_hightemp;
		var time0_lowtemp = data.currentWeather.time0_lowtemp;
		var time0_icon = data.currentWeather.time0_icon;

		var time1 = data.currentWeather.time1;
		var time1_hightemp = data.currentWeather.time1_hightemp;
		var time1_lowtemp = data.currentWeather.time1_lowtemp;
		var time1_icon = data.currentWeather.time1_icon;

		var time2 = data.currentWeather.time2;
		var time2_hightemp = data.currentWeather.time2_hightemp;
		var time2_lowtemp = data.currentWeather.time2_lowtemp;
		var time2_icon = data.currentWeather.time2_icon;

		var time3 = data.currentWeather.time3;
		var time3_hightemp = data.currentWeather.time3_hightemp;
		var time3_lowtemp = data.currentWeather.time3_lowtemp;
		var time3_icon = data.currentWeather.time3_icon;

		var time4 = data.currentWeather.time4;
		var time4_hightemp = data.currentWeather.time4_hightemp;
		var time4_lowtemp = data.currentWeather.time4_lowtemp;
		var time4_icon = data.currentWeather.time4_icon;

		var time5 = data.currentWeather.time5;
		var time5_hightemp = data.currentWeather.time5_hightemp;
		var time5_lowtemp = data.currentWeather.time5_lowtemp;
		var time5_icon = data.currentWeather.time5_icon;

		// Update the html elements with the data
		$('.weather-current-temp').text(temperature + String.fromCharCode(176));
		$('#weather-current-img').attr('src', '/static/' + icon);
		$('.weather-current-title').text(title);
		$('.weather-current-desc').text(desc);
		$('.weather-week-summary').text(week);

		$('.time0').text(time0);
		$('.time0_hightemp').text(time0_hightemp + String.fromCharCode(176));
		$('.time0_lowtemp').text(time0_lowtemp + String.fromCharCode(176));
		$('#time0-img').attr('src', '/static/' + icon);

		$('.time1').text(time1);
		$('.time1_hightemp').text(time1_hightemp + String.fromCharCode(176));
		$('.time1_lowtemp').text(time1_lowtemp + String.fromCharCode(176));
		$('#time1-img').attr('src', '/static/' + icon);

		$('.time2').text(time2);
		$('.time2_hightemp').text(time2_hightemp + String.fromCharCode(176));
		$('.time2_lowtemp').text(time2_lowtemp + String.fromCharCode(176));
		$('#time2-img').attr('src', '/static/' + icon);

		$('.time3').text(time3);
		$('.time3_hightemp').text(time3_hightemp + String.fromCharCode(176));
		$('.time3_lowtemp').text(time3_lowtemp + String.fromCharCode(176));
		$('#time3-img').attr('src', '/static/' + icon);

		$('.time4').text(time4);
		$('.time4_hightemp').text(time4_hightemp + String.fromCharCode(176));
		$('.time4_lowtemp').text(time4_lowtemp + String.fromCharCode(176));
		$('#time4-img').attr('src', '/static/' + icon);

		$('.time5').text(time5);
		$('.time5_hightemp').text(time5_hightemp + String.fromCharCode(176));
		$('.time5_lowtemp').text(time5_lowtemp + String.fromCharCode(176));
		$('#time5-img').attr('src', '/static/' + icon);




	});

}

update_weather();

setInterval(update_weather, 600000);