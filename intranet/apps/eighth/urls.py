# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from .views import routers, signup, attendance
from .views.admin import (
    general, activities, blocks, groups, rooms, sponsors, scheduling)
from .views.admin import attendance as admin_attendance

urlpatterns = [
    url(r"^$", routers.eighth_redirect_view, name="eighth_redirect"),

    # Students
    url(r"^/signup(?:/(?P<block_id>\d+))?$", signup.eighth_signup_view, name="eighth_signup"),

    # Teachers
    url(r"^/attendance$", attendance.teacher_choose_scheduled_activity_view, name="eighth_attendance_choose_scheduled_activity"),
    url(r"^/attendance/(?P<scheduled_activity_id>\d+)$", attendance.take_attendance_view, name="eighth_take_attendance"),
    url(r"^/attendance/accept_pass/(?P<signup_id>\d+)$", attendance.accept_pass_view, name="eighth_accept_pass"),
    url(r"^/attendance/accept_all_passes/(?P<scheduled_activity_id>\d+)$", attendance.accept_all_passes_view, name="eighth_accept_all_passes"),

    # Admin
    url(r"^/admin$", general.eighth_admin_dashboard_view, name="eighth_admin_dashboard"),
]

eighth_admin_patterns = [
    # Activities
    url(r"^activities/add$", activities.add_activity_view, name="eighth_admin_add_activity"),
    url(r"^activities/edit/(?P<activity_id>\d+)$", activities.edit_activity_view, name="eighth_admin_edit_activity"),
    url(r"^activities/delete/(?P<activity_id>\d+)$", activities.delete_activity_view, name="eighth_admin_delete_activity"),

    # Blocks
    url(r"^blocks/add$", blocks.add_block_view, name="eighth_admin_add_block"),
    url(r"^blocks/print_rosters/(?P<block_id>\d+)$", general.not_implemented_view, name="eighth_admin_print_block_rosters"),
    url(r"^blocks/edit/(?P<block_id>\d+)$", blocks.edit_block_view, name="eighth_admin_edit_block"),

    # Scheduling
    url(r"^scheduling/schedule$", scheduling.schedule_activity_view, name="eighth_admin_schedule_activity"),
    url(r"^scheduling/activity_schedule$", scheduling.show_activity_schedule_view, name="eighth_admin_view_activity_schedule"),
    url(r"^scheduling/transfer_students$", scheduling.transfer_students_view, name="eighth_admin_transfer_students"),

    # Attendance
    url(r"^attendance$", attendance.admin_choose_scheduled_activity_view, name="eighth_admin_attendance_choose_scheduled_activity"),
    url(r"^attendance/(?P<scheduled_activity_id>\d+)$", attendance.take_attendance_view, name="eighth_admin_take_attendance"),
    url(r"^attendance/delinquent_students$", admin_attendance.delinquent_students_view, name="eighth_admin_view_delinquent_students"),
    url(r"^attendance/delinquent_students/csv$", admin_attendance.delinquent_students_view, name="eighth_admin_download_delinquent_students_csv"),
    url(r"^attendance/after_deadline_signups$", admin_attendance.after_deadline_signup_view, name="eighth_admin_view_after_deadline_signups"),
    url(r"^attendance/no_attendance$", admin_attendance.activities_without_attendance_view, name="eighth_admin_view_activities_without_attendance"),
    url(r"^attendance/reject_outstanding_passes$", admin_attendance.reject_outstanding_passes_view, name="eighth_admin_reject_outstanding_passes"),
    url(r"^attendance/export_out_of_building_schedules$", admin_attendance.out_of_building_schedules_view, name="eighth_admin_export_out_of_building_schedules"),
    url(r"^attendance/export_out_of_building_schedules/csv/(?P<block_id>\d+)$", admin_attendance.out_of_building_schedules_view, name="eighth_admin_export_out_of_building_schedules_csv"),

    # Groups
    url(r"^groups/add$", groups.add_group_view, name="eighth_admin_add_group"),
    url(r"^groups/edit/(?P<group_id>\d+)$", groups.edit_group_view, name="eighth_admin_edit_group"),
    url(r"^groups/signup/(?P<group_id>\d+)$", groups.eighth_admin_signup_group, name="eighth_admin_signup_group"),
    url(r"^groups/download/(?P<group_id>\d+)$", groups.download_group_csv_view, name="eighth_admin_download_group_csv"),


    # Rooms
    url(r"^rooms/add$", rooms.add_room_view, name="eighth_admin_add_room"),
    url(r"^rooms/edit/(?P<room_id>\d+)$", rooms.edit_room_view, name="eighth_admin_edit_room"),
    url(r"^rooms/sanity_check$", rooms.room_sanity_check_view, name="eighth_admin_room_sanity_check"),
    url(r"^rooms/block_utilization$", rooms.room_utilization_for_block_view, name="eighth_admin_room_utilization_for_block"),
    url(r"^rooms/utilization$", rooms.room_utilization_view, name="eighth_admin_room_utilization"),


    # Sponsors
    url(r"^sponsors/add$", sponsors.add_sponsor_view, name="eighth_admin_add_sponsor"),
    url(r"^sponsors/edit/(?P<sponsor_id>\d+)$", sponsors.edit_sponsor_view, name="eighth_admin_edit_sponsor"),
    url(r"^sponsors/delete/(?P<sponsor_id>\d+)$", sponsors.delete_sponsor_view, name="eighth_admin_delete_sponsor"),
    url(r"^sponsors/schedule/(?P<sponsor_id>\d+)$", sponsors.sponsor_schedule_view, name="eighth_admin_sponsor_schedule"),

    url(r"^startdate$", general.edit_start_date_view, name="eighth_admin_edit_start_date"),

]

urlpatterns += [
    url(r"^/admin/", include(eighth_admin_patterns)),
]
