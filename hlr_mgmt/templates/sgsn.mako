# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%namespace name="table_iterator" file="table_iterator.mako"/>

<div class="page-header">
<h2>SGSN Information and Statistics</h2>
</div>

<h3>Version</h3>
% if sgsn_version:
  ${table_iterator.version(sgsn_version)}
% endif

<h3>NS Statistics</h3>
% if ns_statistics:
  ${table_iterator.iterate(ns_statistics, keyword="Encapsulation", keyword_border=False)}
% endif
