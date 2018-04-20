// 让loading效果生效
$('#myButton1').click(function(event) {

        var starttime = parseInt($('#Xaxisa').val());
        var endtime = parseInt($('#Xaxisb').val());
        if(isEmpty(starttime) || isEmpty(endtime)){
            starttime = parseInt($('#id_Xaxisa').val());
            endtime = parseInt($('#id_Xaxisb').val());
        }

        if(starttime < 0 || starttime >24){
            layui.use('layer', function(){
			    var layer = layui.layer;

			    layer.msg('起始时间点输入有误，应在0到24之间', {
				  time: 5000, //5s后自动关闭
				  btn: ['知道了']
			    });
			});
			event.preventDefault();
			return;
        }

        if(endtime < 0 || endtime >24){
            layui.use('layer', function(){
			    var layer = layui.layer;

			    layer.msg('结束时间点输入有误，应在0到24之间', {
				  time: 5000, //5s后自动关闭
				  btn: ['知道了']
			    });
			});
			event.preventDefault();
			return;
        }


        if(endtime < starttime){
            layui.use('layer', function(){
			    var layer = layui.layer;

			    layer.msg('时间段输入有误，起始时间点应小于结束时间点', {
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


//实现动画效果
(function() {

    var width, height, largeHeader, canvas, ctx, circles, target, animateHeader = true;

    // Main
    initHeader();
    addListeners();

    function initHeader() {
        // 初始化画布宽度，自适应
        width = window.innerWidth;
        // 初始化画布高度，等于输入模块div的高度
        height = document.getElementById("input_area").offsetHeight;
        target = {x: 0, y: height};

        largeHeader = document.getElementById('large-header');
        largeHeader.style.height = height+'px';

        canvas = document.getElementById('demo-canvas');
        canvas.width = width;
        canvas.height = height;
        ctx = canvas.getContext('2d');

        // 创建粒子效果
        circles = [];   //存放粒子的数组
        for(var x = 0; x < width*0.5; x++) {
            var c = new Circle();
            circles.push(c);
        }
        animate();
    }

    // Event handling
    function addListeners() {
        window.addEventListener('scroll', scrollCheck);
        window.addEventListener('resize', resize);
    }

    function scrollCheck() {
        if(document.body.scrollTop > height) animateHeader = false;
        else animateHeader = true;
    }

    function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        largeHeader.style.height = height+'px';
        canvas.width = width;
        canvas.height = height;
    }

    function animate() {
        if(animateHeader) {
            ctx.clearRect(0,0,width,height);
            for(var i in circles) {
                circles[i].draw();
            }
        }
        requestAnimationFrame(animate);
    }

    // Canvas manipulation
    function Circle() {
        var _this = this;

        // constructor
        (function() {
            _this.pos = {};
            init();
            console.log(_this);
        })();

        function init() {
            //横坐标位置随机，限定在宽度内即可
            _this.pos.x = Math.random()*width;
            _this.pos.y = height+Math.random()*100;
            //粒子的透明度
            _this.alpha = 0.1+Math.random()*0.3;
            // 粒子的大小
            _this.scale = 0.1+Math.random()*0.3;
            // 粒子的速度
            _this.velocity = Math.random();
        }

        this.draw = function() {
            // 如果粒子透明度小于0，重新初始化
            if(_this.alpha <= 0) {
                init();
            }
            _this.pos.y -= _this.velocity;
            _this.alpha -= 0.0005;
            ctx.beginPath();
            ctx.arc(_this.pos.x, _this.pos.y, _this.scale*10, 0, 2 * Math.PI, false);
            ctx.fillStyle = 'rgba(155,55,25,'+ _this.alpha+')';
            ctx.fill();
        };
    }

})();