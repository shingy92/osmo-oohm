# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>

  <div class="page-header">
  <h2>Management Scripts</h2>
  </div>

  <h3>Register IMSI through IMEI Lookup</h3>
  <h4>This script will lookup the phone with the IMEI provided and authorize its active IMSI (SIM Card) for access</h4>
  <form action="javascript:authorize_imei();" id="imei_form">
    <fieldset>
    <span class="help-block">Dial *#06# on the Target Phone to obtain its IMEI. Then enter the IMEI below.</span>
    <div class="span7">
    <input type="text" placeholder="15 digit IMEI..." name="imei">
    <button type="submit" class="btn btn-info pull-right">Queue Authorization</button>
    </div>
    </fieldset>
  </form>
  <div class="alert alert-error" hidden></div>
  <div class="alert alert-success" hidden></div>
  <br/><br/>
  <h3>Running Services</h3>
  <table class="table table-bordered table-hover" id="scripts_table">
  <thead>
    <tr><th> Service </th>
        <th> Status </th>
	<th> Actions </th>
    </tr>
  </thead>
  <tbody>
     <tr><td>LCR <div class="pull-right">(Local GSM Call Routing)</div></td>
    % if service_status['lcr']:
      % if service_status['lcr'].find("running")>0:
        <td><span class="label label-success">Running</span></td>
      % else:
        <td><span class="label label-important">Stopped</span></td>
      % endif
    % else:
      <td><span class="label label-warning">ERROR</span></td>
    % endif
    <td>
      <start><a href="${request.route_url('manage_service', service='lcr', action=1)}"><span class="badge badge-success"><i class="icon-play icon-white"></i></span></a></start>
      <reload><a href="${request.route_url('manage_service', service='lcr', action=2)}"><span class="badge badge-info"><i class="icon-repeat icon-white"></i></span></a></reload>
      <stop><a href="${request.route_url('manage_service', service='lcr', action=3)}"><span class="badge badge-important"><i class="icon-pause icon-white"></i></span></a></stop>
    </td></tr>
    <tr><td>Asterisk <div class="pull-right">(External Call Routing)</div></td>
    % if service_status['asterisk']:
      % if service_status['asterisk'].find("failed")<0:
        <td><span class="label label-success">Running</span></td>
      % else:
        <td><span class="label label-important">Stopped</span></td>
      % endif
    % else:
      <td><span class="label label-warning">ERROR</span></td>
    % endif
    <td>
      <start><a href="${request.route_url('manage_service', service='asterisk', action=1)}"><span class="badge badge-success"><i class="icon-play icon-white"></i></span></a></start>
      <reload><a href="${request.route_url('manage_service', service='asterisk', action=2)}"><span class="badge badge-info"><i class="icon-repeat icon-white"></i></span></a></reload>
      <stop><a href="${request.route_url('manage_service', service='asterisk', action=3)}"><span class="badge badge-important"><i class="icon-pause icon-white"></i></span></a></stop>
    </td></tr>
    <tr><td>GGSN <div class="pull-right">(GPRS Data Gateway)</div></td>
    % if service_status['ggsn']:
      % if service_status['ggsn'].find("failed")<0:
        <td><span class="label label-success">Running</span></td>
      % else:
        <td><span class="label label-important">Stopped</span></td>
      % endif
    % else:
      <td><span class="label label-warning">ERROR</span></td>
    % endif
    <td>
      <start><a href="${request.route_url('manage_service', service='ggsn', action=1)}"><span class="badge badge-success"><i class="icon-play icon-white"></i></span></a></start>
      <reload><a href="${request.route_url('manage_service', service='ggsn', action=2)}"><span class="badge badge-info"><i class="icon-repeat icon-white"></i></span></a></reload>
      <stop><a href="${request.route_url('manage_service', service='ggsn', action=3)}"><span class="badge badge-important"><i class="icon-pause icon-white"></i></span></a></stop>
    </td></tr>
    <tr><td>OpenBSC <div class="pull-right">(Controls GSM Access)</div></td>
    % if service_status['nitb']:
      % if service_status['nitb'].find("failed")<0:
        <td><span class="label label-success">Running</span></td>
      % else:
        <td><span class="label label-important">Stopped</span></td>
      % endif
    % else:
      <td><span class="label label-warning">ERROR</span></td>
    % endif
    <td>
      <start><a href="${request.route_url('manage_service', service='nitb', action=1)}"><span class="badge badge-success"><i class="icon-play icon-white"></i></span></a></start>
      <reload><a href="${request.route_url('manage_service', service='nitb', action=2)}"><span class="badge badge-info"><i class="icon-repeat icon-white"></i></span></a></reload>
      <stop><a href="${request.route_url('manage_service', service='nitb', action=3)}"><span class="badge badge-important"><i class="icon-pause icon-white"></i></span></a></stop>
    </td></tr>
    <tr><td>OsmoSGSN <div class="pull-right">(GPRS Data Interface)</div></td>
    % if service_status['sgsn']:
      % if service_status['sgsn'].find("failed")<0:
        <td><span class="label label-success">Running</span></td>
      % else:
        <td><span class="label label-important">Stopped</span></td>
      % endif
    % else:
      <td><span class="label label-warning">ERROR</span></td>
    % endif
    <td>
      <start><a href="${request.route_url('manage_service', service='sgsn', action=1)}"><span class="badge badge-success"><i class="icon-play icon-white"></i></span></a></start>
      <reload><a href="${request.route_url('manage_service', service='sgsn', action=2)}"><span class="badge badge-info"><i class="icon-repeat icon-white"></i></span></a></reload>
      <stop><a href="${request.route_url('manage_service', service='sgsn', action=3)}"><span class="badge badge-important"><i class="icon-pause icon-white"></i></span></a></stop>
    </td></tr>
    <tr><td><strong><em>SubscriberMonitor</em></strong> <div class="pull-right">(Greets users with SMS)</div></td>
    % if service_status['subMonitor']:
      <td><span class="label label-success">Running</span></td>
    % else:
      <td><span class="label label-important">Stopped</span></td>
    % endif
    <td>
      <start><a href="${request.route_url('manage_service', service='subMonitor', action=1)}"><span class="badge badge-success"><i class="icon-play icon-white"></i></span></a></start>
      <reload><a href="${request.route_url('manage_service', service='subMonitor', action=2)}"><span class="badge badge-info"><i class="icon-repeat icon-white"></i></span></a></reload>
      <stop><a href="${request.route_url('manage_service', service='subMonitor', action=3)}"><span class="badge badge-important"><i class="icon-pause icon-white"></i></span></a></stop>
    </td></tr>
  </tbody>
  </table>

<script>
function authorize_imei()
{
	url = "${request.route_url('authorize_imei',imei='000000000000000')}";
	form_input = $('#imei_form :input');
	imei = form_input.val()
	url = url.replace("000000000000000",imei)
	$.ajax({
		url: url,
		success: function(data){
			switch(data.success)
			{
				case 1:
					$(".alert-success").append("<strong>SUCCESS:</strong> Registration of SIM card in device with IMEI:" + imei + " queued!<br/>");
					$(".alert-success").show();
					break;
				case 0:
					$(".alert-error").append("<strong>Invalid IMEI:</strong> IMEI:" + imei + " has incorrect FORMAT<br/>");
				case -1:
					$(".alert-error").append("<strong>Invalid IMEI:</strong> IMEI:" + imei + " has incorrect LENGTH<br/>");
				case -2:
					$(".alert-error").append("<strong>Invalid IMEI:</strong> IMEI:" + imei + " has incorrect CHECKSUM DIGIT<br/>");
					$(".alert-error").show();
				default:
					break;
			}
			setTimeout("close_alerts()",5000);
		}
	})
}

$("#scripts_table start").tooltip({
	title: 'Click to Start',
	placement: 'right'
});
$("#scripts_table stop").tooltip({
        title: 'Click to Stop',
        placement: 'right'
});
$("#scripts_table reload").tooltip({
        title: 'Click to Reload',
        placement: 'right'
});
</script>
