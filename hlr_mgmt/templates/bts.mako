# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%namespace name="table_iterator" file="table_iterator.mako"/>

<div class="page-header">
<h2>BTS Detailed Information</h2>
% if bts:
  <h4>Number of Deployed BTS: ${len(bts)}</h4>
% endif
</div>

% if bts and phys_cfg:
  <ul class="nav nav-tabs">
  % for i in range(0,len(bts)):
       % if bts[i]['oml_state']:
          % if bts[i].has_key('ip'):
             <li><a href="#bts_${i}" data-toggle="tab"><h5><span class="badge badge-success"><i class="icon-map-marker icon-white"></span></i> BTS ${i}</h5></a></li>
          % else:          
             <li><a href="#bts_${i}" data-toggle="tab"><h5><span class="badge badge-warning"><i class="icon-warning-sign icon-white"></span></i> BTS ${i}</h5></a></li>
          % endif
       % else:
             <li><a href="#bts_${i}" data-toggle="tab"><h5><span class="badge badge-important"><i class="icon-exclamation-sign icon-white"></span></i> BTS ${i}</h5></a></li>
       % endif
  % endfor
  </ul>
  <div class="tab-content">
    % for i in range(0,len(bts)):
      % if i==0:
        <div class="tab-pane" id="bts_${i}">
      % else:
        <div class="tab-pane" id="bts_${i}">
      % endif
          <h3>BTS ${i}
          % if bts[i]['oml_state']:
            % if bts[i].has_key('ip'):
              (${bts[i]['ip']})
            % else:
              (OML connected without IP address)
            % endif
          % else:
            (OML disconnected)
          % endif
          <br/><bts_description data-pk="${i}">${bts[i]['description']}</bts_description>
          </h3>
        ${table_iterator.iterate(bts[i]['stats'])}
        <h3>Channel Details</h3>
        <div class="alert alert-error" hidden></div>
        <div class="alert alert-success" hidden></div>
        <table class="table table-hover table-condensed">
          <thead>
          <tr>
            <th>phys cfg</th>
            <th>TSC</th>
            <th>NM State</th>
            <th>Admin</th>
            <th>Avail</th>
          </tr>
          </thead>
          <tbody>
          % for j in range(0,len(bts[i]['timeslots'])):
            <tr>
            % for detail in bts[i]['timeslots'][j]:
              % if detail.find("phys")>=0:
                 <td><select onChange="toggle_channel(${i},${j})" id="config_${i}_${j}">
                 % for setting in phys_cfg:
                   % if setting==detail.split(": ")[1]:
                     <option selected value="${setting}">${setting}</option>
                   % else:
                     <option value="${setting}">${setting}</option>
                   % endif
                 % endfor
                 </select></td>
              % else:
                % if detail.find(": ")>0:
                  <td>${detail.split(": ")[1]}</td>
                % else:
                  <td>${' '.join(detail.split()[1:])}</td>
                % endif
              % endif
            % endfor
            </tr>
          % endfor
          </tbody>
        </table>
	<br/>
	% if bts[i].has_key('bssgp'):
           <h3>BSSGP Data Connection Details</h3>
           ${table_iterator.iterate(bts[i]['bssgp'])}
           </br><h3>NSEI Data Connection Details</h3>
           ${table_iterator.iterate(bts[i]['nsei'][:-1])}
           </br>
        % endif
      </div>
    % endfor
  </div>
  </ul>
% else:
  <h4>No BTS deployed</h4>
% endif

<script>

function linkedTab()
{
	//function which handles linking to tabular content
	hash = location.hash
	hash = hash.split('?')[0]
	activeTab = $('[href=' + hash + ']');
	activeTab.tab('show');
}
linkedTab();

function toggle_channel(bts_id,channel)
{
       var modified = document.getElementById("config_"+bts_id+"_"+channel);
       var config = modified.options[modified.selectedIndex].text;
       var url = '${request.route_url('toggle_channel',bts_id='bts_id',channel='channel')}';
       url = url.replace('bts_id',bts_id);
       url = url.replace('channel',channel);
       url = url + "?config=" + config
       $.ajax({
               url: url,
               success: function(){
                       $(".alert-success").append("<strong>SUCCESS:</strong> BTS " + bts_id + " successfully changed configuration for channel " + channel + " to " + config + "<br/>");
                       $(".alert-success").show();
	               setTimeout("close_alerts()",5000);
               },
               error: function(){
                       $(".alert-error").append("<strong>ERROR:</strong> BTS " + bts_id + " was not able to change the configuration for channel " + channel + " to " + config + "<br/>");
                       $(".alert-error").show();
                       setTimeout("close_alerts()",5000);
               }
       });
}

$('select').tooltip({
        placement: "left",
        title: "Select desired channel configuration"
});

$('bts_description').tooltip({
        placement: "right",
        title: "Click to Edit this Description"
});

$('bts_description').editable({
        type: 'text',
        placement: 'bottom',
        title: 'Edit the Description of this BTS',
        emptytext: '____',
        inputclass: 'span3',
        url: function(params)
        {
                $.ajax({
                        url: '${request.route_url('rename_component',field='bts',value='val',reference='ref')}'.replace('ref/val', params.pk+'/'+params.value)
                });
         }
});

</script>
