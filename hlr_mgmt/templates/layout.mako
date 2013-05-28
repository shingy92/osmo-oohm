# -*- coding: utf-8 -*- 
<!DOCTYPE html>  
<html>
<head>
	
  <meta charset="utf-8">
  <title>OpenBSC and OsmoSGSN HLR Management Interface</title>
  <link rel="shortcut icon" href="/static/images/favicon.ico" />
  
  <link rel="stylesheet" href="/static/bootstrap/css/bootstrap.css">
  <link rel="stylesheet" href="/static/bootstrap/css/bootstrap-responsive.css">
  <link rel="stylesheet" href="/static/bootstrap/css/docs.css">
  <link rel="stylesheet" href="/static/bootstrap-editable/css/bootstrap-editable.css">
  <link rel="stylesheet" href="/static/DataTables/DT_bootstrap.css">
  <link rel="stylesheet" href="/static/style.css">

  <script src="/static/bootstrap/js/jquery.js"></script>
  <script src="/static/bootstrap/js/bootstrap-transition.js"></script>
  <script src="/static/bootstrap/js/bootstrap-alert.js"></script>
  <script src="/static/bootstrap/js/bootstrap-modal.js"></script>
  <script src="/static/bootstrap/js/bootstrap-dropdown.js"></script>
  <script src="/static/bootstrap/js/bootstrap-scrollspy.js"></script>
  <script src="/static/bootstrap/js/bootstrap-tab.js"></script>
  <script src="/static/bootstrap/js/bootstrap-tooltip.js"></script>
  <script src="/static/bootstrap/js/bootstrap-popover.js"></script>
  <script src="/static/bootstrap/js/bootstrap-button.js"></script>
  <script src="/static/bootstrap/js/bootstrap-collapse.js"></script>
  <script src="/static/bootstrap/js/bootstrap-carousel.js"></script>
  <script src="/static/bootstrap/js/bootstrap-typeahead.js"></script>
  <script src="/static/bootstrap-editable/js/bootstrap-editable.js"></script>
  <script src="/static/DataTables/jquery.dataTables.js"></script>
  <script src="/static/DataTables/DT_bootstrap.js"></script>

</head>
<body>
  <div class="fluid-container">
    <div class="fluid-row">
      <div class="span2 affix" style="height:100%;">
            <a href="http://www.fokus.fraunhofer.de/de/rescon/index.html">
            <img src="/static/images/FOKUS.png">
            </a>
            <ul class="nav nav-list bs-docs-sidenav">
              % if request.path=="/":
                <li class="active">
                  <a href="/"><i class="icon-home icon-white">
              % else:
                <li>
                  <a href="/"><i class="icon-home icon">
              % endif
              </i> Home <i class="icon-chevron-right"></i></a></li>
              % if request.path.find("/bsc/")==0:
                 <li class="active">
                   <a href="/bsc/"><i class="icon-signal icon-white">
              % else:
                <li>
                   <a href="/bsc/"><i class="icon-signal icon">
              % endif
              </i> BSC Stats <i class="icon-chevron-right"></i></a></li>
              % if request.path.find("/sgsn/")==0:
                 <li class="active">
                   <a href="/sgsn/"><i class="icon-globe icon-white">
              % else:
                 <li>
                   <a href="/sgsn/"><i class="icon-globe icon">
              % endif
              </i> SGSN Stats <i class="icon-chevron-right"></i></a></li>
              % if request.path.find("/bts/")==0:
                 <li class="active">
                   <a href="/bts/"><i class="icon-road icon-white">
              % else:
                 <li>
                   <a href="/bts/"><i class="icon-road icon">
              % endif
              </i> BTS Config <i class="icon-chevron-right"></i></a></li>
              % if request.path.find("/subscribers/")==0:
                 <li class="active">
                   <a href="/subscribers/"><i class="icon-user icon-white">
              % else:
                 <li>
                   <a href="/subscribers/"><i class="icon-user icon">
              % endif
              </i> Subscribers <i class="icon-chevron-right"></i></a></li>
              % if request.path.find("/sms/")==0:
                 <li class="active">
                   <a href="/sms/"><i class="icon-envelope icon-white">
              % else:
                 <li>
                   <a href="/sms/"><i class="icon-envelope icon">
              % endif
              </i> SMS <i class="icon-chevron-right"></i></a></li>
              % if request.path.find("/scripts/")==0:
                 <li class="active">
                   <a href="/scripts/"><i class="icon-cog icon-white">
              % else:
                 <li>
                   <a href="/scripts/"><i class="icon-cog icon">
              % endif
              </i> Mgmt Scripts <i class="icon-chevron-right"></i></a></li>
             </ul><!--nav-->
             <div style="position: absolute; bottom: 100px; left: 0;">
             <a id="logo" href="http://openbsc.osmocom.org/"><img src="http://bb.osmocom.org/osmocom/osmocom_logo.png" style="width:170px"/></a>
             </div>
      </div><!--span2-->
      <div class="span10 offset2" style="padding-bottom:35px">
      <script>
        function close_alerts()
        {
           $(".alert").html("")
           $(".alert").hide()
        }
      </script>
      ${next.body()}
      </div>
      <div class="navbar-fixed-bottom" style="background:#009473">
        <div class="pull-right"><a href="http://www.pylonsproject.org/"><img src="http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/_static/pyramid-small.png" style="height:30px"/></a></div>
	<center><a rel="license" href="http://creativecommons.org/licenses/by-sa/3.0/"><img alt="Creative Commons License" src="http://i.creativecommons.org/l/by-sa/3.0/88x31.png" style="height:30px"/></a></center>
      </div>
    </div>
    </div>
</body>
</html>
