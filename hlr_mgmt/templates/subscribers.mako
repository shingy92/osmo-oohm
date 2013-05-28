# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>

<div class="page-header">
<h1>Subscribers</h1>
<h3>List of Previously Active Subscribers</h3>
<h4>(does not contain all SIM cards detected by OpenBSC)</h4>
</div>
<div class="alert alert-error" hidden></div>
<div class="alert alert-success" hidden></div>
<table class="table table-bordered table-hover" id="subscribers_table">
<thead>
  <tr><th style="padding-right: 20px;"> Extension </th>
      <th style="padding-right: 20px;"> SIM Name </th>
      <th style="padding-right: 20px;"> Created </th>
      <th style="padding-right: 20px;"> IMSI </th>
      <th style="padding-right: 20px;"> Country </th>
      <th style="padding-right: 20px;"> Operator </th>
      <th style="padding-right: 20px;"> TMSI </th>
      <th style="padding-right: 20px;"> Attached </th>
      <th style="padding-right: 20px;"> Authorized </th>
  </tr>
</thead>
<tbody>
% if subscribers:
  % for sub in subscribers:
  <tr>
    <td><extension><a href="${request.route_url('subscriber_detail', extension=sub['ext'])}">${sub['ext']}</a></extension></td>
    <td><imsi_name data-pk="${sub['imsi']}">${sub['name']}</imsi_name></td>
    <td>${sub['created']}</td>
    <td>${sub['imsi']}</td>
    % if sub['operator']== None:
      <td></td><td></td>
    % else:
      <td>${sub['operator'][0]}</td><td>${sub['operator'][1]}</td>
    % endif
    <td>
      % if not sub['tmsi']== None:
        ${hex(int(str(sub['tmsi']),10))}
      % endif
    </td>
    <td>
      % if sub['lac'] > 0:
        <span class="label label-success">LAC: ${sub['lac']}</span>
      % else:
        <span class="label">Inactive</span>
      % endif
    </td>
    <td><authorized><a href="javascript:auth_toggle(${sub['ext']});" id="auth_${sub['ext']}"><div class="hidden">
      % if sub['authorized']==1:
        1</div><span class="badge badge-success"><i class="icon-ok icon-white">
      % else:
        0</div><span class="badge badge-important"><i class="icon-remove icon-white">
      % endif
    </i></span></a></authorized></td>
  </tr>
  % endfor
% endif
</tbody>
</table>
<script>
function auth_toggle(ext) {
	url = "${request.route_url('authorize_toggle', extension='ext')}";
	url = url.replace('ext',ext);
	$.ajax({
		url: url,
		success: function() {
			html = $("#auth_" + ext).html();	
			if (html.indexOf("1")>0)
				auth_html="<div class='hidden'>0</div><span class='badge badge-important'><i class='icon-remove icon-white'></i></span>";
			else
				auth_html="<div class='hidden'>1</div><span class='badge badge-success'><i class='icon-ok icon-white'></i></span>";
			$("#auth_" + ext).html(auth_html);
		},
		error: function() {
			$(".alert-error").append("<strong>ERROR:</strong> Could not change Authorization Status for Extension: " + ext + "<br/>");
			$(".alert-error").show();
			setTimeout("close_alerts()",5000);
		}
	})
}

$(document).ready(function() {
    $('#subscribers_table').dataTable( {
        "sDom": "<'row'<'span5'l><'span5'f>r>t<'row'<'span5'i><'span5'p>>"
    } );
} );

$.extend( $.fn.dataTableExt.oStdClasses, {
    "sWrapper": "dataTables_wrapper form-inline"
} );

$('#subscribers_table extension').tooltip({
        placement: "left",
        title: "Click here for Details"
});

$('#subscribers_table authorized').tooltip({
	placement: "right",
	title: "Click to Toggle Authorization ON or OFF"
});

$('#subscribers_table imsi_name').tooltip({
        placement: "right",
        title: "Click to Edit this IMSI Name"
});

$('#subscribers_table imsi_name').editable({
        type: 'text',
        placement: 'bottom',
        title: 'Edit the name for this IMSI',
        emptytext: '____',
        url: function(params)
        {
                $.ajax({
                        url: '${request.route_url('rename_component',field='imsi',value='val',reference='ref')}'.replace('ref/val', params.pk+'/'+params.value)
                });
         }
});
</script>
