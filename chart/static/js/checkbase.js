// 让loading效果生效
$('#myButton1').click(function(event) {
		$(this).button('loading');
	});

// 放大缩小会堆叠的根本原因是input框、select框、textarea框都是后台生成的，没有设置class="form-control"
$("input").addClass("form-control ");
$("select").addClass("form-control");
$("textarea").addClass("form-control");

