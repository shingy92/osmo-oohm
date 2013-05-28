# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>

<div class="page-header">
<h2>SMS</h2>
</div>

<h3>Broadcast SMS</h3>
<h5>* Messages are automatically truncated at 160 characters!</h5>
  <form action="${request.route_url('broadcast_sms')}">
  <fieldset>
  <textarea class="span10" placeholder="write a message..." name="text"></textarea>
  <button type="submit" class="btn btn-info pull-right">Send Broadcast SMS</button>
  </fieldset>
</form>

<a href="${request.route_url('clear_sms')}" class="btn btn-danger">Clear SMS History</a>

<br/><br/>

<h3>History</h3>
<table class="table table-bordered table-hover">
<thead>
  <tr><th> ID </th>
      <th> From </th>
      <th> To </th>
      <th> Sent </th>
      <th> Delivered </th>
      <th> Message </th>
      <th> Actions </th>
  </tr>
</thead>
<tbody>
% if sms:
  % for msg in sms:
  <tr>
    <td>${msg['id']}</td>
    <td><a href="${request.route_url('subscriber_detail', extension=msg['from_id'])}">${msg['from_id']}</a></td>
    <td><a href="${request.route_url('subscriber_detail', extension=msg['to_id'])}">${msg['to_id']}</a></td>
    <td>${msg['sent']}</td>
    <td>${msg['delivered']}</td>
    <td>${msg['message']}</td>
    <td><a href="${request.route_url('delete_sms', id=msg['id'])}">Delete</a></td>
  </tr>
  % endfor
% endif
<tbody>
</table>
