# -*- coding: utf-8 -*-

<%def name="version(version_iterable)">
  % for entry in version_iterable:
    ${entry}<br/>
  % endfor
</%def>

<%def name="iterate(data, keyword='', keyword_border=True,subdiv=False)">
  <table>
  % for entry in data:
    % if entry.find(keyword)>=0 and len(keyword)>0:
      %if keyword_border:
        <tr class="border-bottom"><td colspan=2><strong>${entry.strip()}</strong></td></tr>
      %else:
        <tr><td colspan=2><strong>${entry.strip()}</strong></td></tr>
      %endif
    % elif len(entry.split(": "))==2 and len(entry.split(":"))==2:
      <tr><td><strong>${entry.split(": ")[0]}</strong></td><td>${entry.split(": ")[1]}</td></tr>
    % elif subdiv and len(entry.split(": "))>2:
      % for detail in entry.split(", "):
        <tr><td><strong>${detail.split(": ")[0]}</strong></td><td>${detail.split(": ")[1]}</td></tr>
      % endfor
    % else :
      <tr class="border-bottom"><td colspan=2><strong>${entry.strip()}</strong></td></tr>
    % endif
  % endfor
  </table>
</%def>
