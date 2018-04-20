// 让loading效果生效
$('#myButton1').click(function(event) {

	var endyear = parseInt($('#endyear').val());
		var startyear = parseInt($('#originyear').val());
		if(isEmpty(endyear) || isEmpty(startyear)){
			endyear = parseInt($('#id_endyear').val());
			startyear = parseInt($('#id_originyear').val());
		}


		var endmonth = parseInt($('#endmonth').val());
		var startmonth = parseInt($('#originmonth').val());
		if(isEmpty(endmonth) || isEmpty(startmonth)){
			endmonth = parseInt($('#id_endmonth').val());
			startmonth = parseInt($('#id_originmonth').val());
		}

		var endday = parseInt($('#endday').val());
		var startday = parseInt($('#originday').val());
		if(isEmpty(endday) || isEmpty(startday)){
			endday = parseInt($('#id_endday').val());
		    startday = parseInt($('#id_originday').val());
		}

		var endhour = parseInt($('#endhour').val());
		var starthour = parseInt($('#originhour').val());
		if(isEmpty(endday) || isEmpty(startday)){
			endhour = parseInt($('#id_endhour').val());
		    starthour = parseInt($('#id_originhour').val());
		}

		var endmin = parseInt($('#endmin').val());
		var startmin = parseInt($('#originmin').val());
		if(isEmpty(endday) || isEmpty(startday)){
			endmin = parseInt($('#id_endmin').val());
		    startmin = parseInt($('#id_originmin').val());
		}

		if(endyear < startyear){

			layui.use('layer', function(){
			    var layer = layui.layer;

			    layer.msg('数据输入有误！起始年份应小于结束年份', {
				  time: 5000, //5s后自动关闭
				  btn: ['知道了']
			    });
			});
			event.preventDefault();
			return;
		}

		if(endmonth < startmonth){

			layui.use('layer', function(){
			    var layer = layui.layer;

			    layer.msg('数据输入有误！起始月份应小于结束月份', {
				  time: 5000, //5s后自动关闭
				  btn: ['知道了']
			    });
			});
			event.preventDefault();
			return;
		}

		if(endday < startday){

			layui.use('layer', function(){
			    var layer = layui.layer;

			    layer.msg('数据输入有误！起始日期应小于结束日期', {
				  time: 5000, //5s后自动关闭
				  btn: ['知道了']
			    });
			});
			event.preventDefault();
			return;
		}


		if(starthour < 0 || starthour>24){
			layui.use('layer', function(){
			    var layer = layui.layer;

			    layer.msg('小时输入有误，应在0到24之间', {
				  time: 5000, //5s后自动关闭
				  btn: ['知道了']
			    });
			});
			event.preventDefault();
			return;
		}


		if(startmin < 0 || startmin>60){
			layui.use('layer', function(){
			    var layer = layui.layer;

			    layer.msg('分钟输入有误，应在0到24之间', {
				  time: 5000, //5s后自动关闭
				  btn: ['知道了']
			    });
			});
			event.preventDefault();
			return;
		}


		if(endhour < starthour){

			layui.use('layer', function(){
			    var layer = layui.layer;

			    layer.msg('数据输入有误！起始小时应小于结束小时', {
				  time: 5000, //5s后自动关闭
				  btn: ['知道了']
			    });
			});
			event.preventDefault();
			return;
		}

		if(endmin < startmin){

			layui.use('layer', function(){
			    var layer = layui.layer;

			    layer.msg('数据输入有误！起始分钟应小于结束分钟', {
				  time: 5000, //5s后自动关闭
				  btn: ['知道了']
			    });
			});
			event.preventDefault();
			return;
		}


		$(this).button('loading');
	});

function isEmpty(str) {
	if(str == undefined || str.length == 0 || str == null || isNaN(str)){
		return true;
	}

	return false;
}


// 放大缩小会堆叠的根本原因是input框、select框、textarea框都是后台生成的，没有设置class="form-control"
$("input").addClass("form-control");
$("select").addClass("form-control");
$("textarea").addClass("form-control");