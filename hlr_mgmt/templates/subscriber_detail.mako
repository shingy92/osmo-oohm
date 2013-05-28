# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%namespace name="table_iterator" file="table_iterator.mako"/>

% if extension>=20000 and extension<=49999:
  <h2>Subscriber Extension: ${extension}</h2>

  <h3>Used by Handsets with IMEI:</h3>
  <h5>* IMEI values are stored in the database without the checksum digit. (i.e. it replaces the last digit shown here with 0)</h5>
  <table class="table table-bordered table-hover" id="subscriber_details">
  <thead>
    <tr><th> IMEI </th>
	<th> Equipment Name </th>
	<th> Last Used </th>
    </tr>
  </thead>
  <tbody>
  % if subscriber:
    % for handset in subscriber:
    <tr>
      <td>${handset['imei']}</td>
      <td>
        <imei_name data-pk="${handset['imei'][:-1]+'0'}">
        % if not handset['name']==None:
          ${handset['name']}
        %endif
        </imei_name>
      </td>
      <td>${handset['updated']}</td>
    </tr>
    % endfor
  % endif
  <tbody>
  </table>

  <h3>Send SMS</h3>
  <h5>* Messages are automatically truncated at 160 characters!</h5>
    <form action="${request.route_url('send_sms',extension=extension)}">
    <fieldset>
    <textarea class="span10" placeholder="write a message..." name="text"></textarea>
    <button type="submit" class="btn btn-info pull-right">Send</button>
    </fieldset>
  </form>

  % if not mm==None:
    % if len(mm)>3:
      <h3>Active Data Connection Details:</h3>
      ${table_iterator.iterate(mm[:-1], keyword="IMSI", subdiv=True)}
    % endif
  % endif
% else:
  <h1>Invalid Extension: ${extension}</h1>
  
% endif

<script>
$('#subscriber_details imei_name').tooltip({
        placement: "right",
        title: "Click to Edit this IMEI Name"
});

$('#subscriber_details imei_name').editable({
        type: 'text',
        placement: 'bottom',
        title: 'Edit the name for this IMEI',
        emptytext: '____',
        url: function(params)
        {
                $.ajax({
                        url: '${request.route_url('rename_component',field='imei',value='val',reference='ref')}'.replace('ref/val', params.pk+'/'+params.value)
                });
         }
});
</script>
