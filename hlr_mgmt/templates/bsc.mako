# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%namespace name="table_iterator" file="table_iterator.mako"/>

<div class="page-header">
<h2>BSC Information and Statistics</h2>
</div>

<h3>Version</h3>
% if bsc_version:
  ${table_iterator.version(bsc_version)}
% endif

<h3>Network</h3>

% if bsc_network:
  ${table_iterator.iterate(bsc_network)}
% endif

<h3>Statistics</h3>
% if bsc_statistics:
  ${table_iterator.iterate(bsc_statistics)}
% endif

