# TeamFlow User Guide

This guide explains how to use TeamFlow for team task management, project tracking, and performance monitoring.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard](#dashboard)
3. [Projects](#projects)
4. [Tasks](#tasks)
5. [Milestones](#milestones)
6. [Timeline](#timeline)
7. [Performance](#performance)
8. [Schedule](#schedule)
9. [Team](#team)
10. [Updates](#updates)
11. [Board](#board)
12. [AI Assistant](#ai-assistant)

## Getting Started

### Account Setup

1. Navigate to the TeamFlow URL
2. Click "Register" to create a new account
3. Fill in your email, username, full name, and password
4. Click "Create Account"
5. You'll be logged in automatically

### Login

1. Navigate to the TeamFlow URL
2. Click "Login"
3. Enter your email and password
4. Click "Sign In"

## Dashboard

The dashboard provides an overview of your work and team status.

### What You'll See

**My Tasks Section:**
- Your assigned tasks sorted by urgency
- Overdue tasks highlighted in red
- Tasks due within 48 hours highlighted
- Click any task to view details

**Team Health Section** (Supervisor/Assistant Manager/Manager only):
- Workload status for each team member
- Overloaded/healthy/underloaded indicators
- At-risk members visually distinguished

**KPI Summary Strip** (Supervisor/Assistant Manager/Manager only):
- Average team KPI score
- Task completion rate
- Number of members needing attention
- Click to view full performance details

**Recent Activity Feed:**
- Latest standup posts from your team
- Shows author name, post summary, and relative time
- Click to view full updates page

### Navigating the Dashboard

- **Task Cards:** Click to navigate to task details
- **KPI Strip:** Click to view performance page
- **Team Health:** Click to view full performance page
- **Activity Items:** Click to view updates page

## Projects

Projects organize tasks and milestones under a common goal.

### Creating a Project

1. Navigate to the Projects page
2. Click "New Project"
3. Fill in:
   - Project name
   - Description
   - Color (for visual identification)
4. Click "Create Project"

### Viewing Projects

- Projects are displayed as cards with name, description, and color
- Click a project to view its tasks and milestones
- Filter projects by status or search by name

### Managing Projects

- **Edit:** Click the edit icon on a project card
- **Delete:** Click the delete icon (requires confirmation)
- **View Tasks:** Click on project to see associated tasks

## Tasks

Tasks are the core work items in TeamFlow.

### Creating a Task

1. Navigate to the Tasks page
2. Click "New Task"
3. Fill in:
   - Title (required)
   - Description
   - Priority (Low, Medium, High, Critical)
   - Status (To Do, In Progress, Review, Done, Blocked)
   - Due date
   - Assignee
   - Project
   - Milestone
   - Tags
4. Click "Create Task"

### Using AI Task Input

1. Click the AI button in the task creation form
2. Describe your task in natural language
3. TeamFlow AI will extract fields automatically
4. Review and edit the extracted information
5. Click "Create Task"

### Task Views

**List View:**
- All tasks in a table format
- Sort by any column
- Filter by status, priority, assignee, project

**Kanban Board:**
- Tasks organized by status columns
- Drag and drop to change status
- Visual workflow management

**Sprint View:**
- Tasks organized by sprint
- Sprint progress indicators
- Burndown-style visualization

### Updating a Task

1. Click on a task to open details
2. Edit any field
3. Click "Save Changes"
4. Status changes trigger automatic KPI updates

### Task Priorities

- **Critical:** Immediate attention required
- **High:** Important but not urgent
- **Medium:** Normal priority
- **Low:** Nice to have, can be deferred

### Task Status Workflow

```
To Do → In Progress → Review → Done
                ↓
             Blocked
```

- Blocked tasks indicate impediments
- Move back to To Do or In Progress when unblocked

## Milestones

Milestones track major deliverables and releases.

### Creating a Milestone

1. Navigate to the Milestones page
2. Click "New Milestone"
3. Fill in:
   - Title
   - Description
   - Project
   - Status (Planned, In Progress, Completed)
   - Start date
   - Due date
4. Click "Create Milestone"

### Milestone Planning

Each milestone has a planning section for:
- Decisions made
- Related tasks
- Progress tracking

### Viewing Milestone Progress

- Progress bar shows completion percentage
- Linked tasks display completion status
- Timeline view shows milestone in context

## Timeline

The timeline provides a Gantt-style view of project progress.

### Using the Timeline

- **Milestone View:** See all milestones with start/end dates
- **Task Rollup:** Tasks linked to milestones appear under them
- **Planning Signals:** Decisions and status indicators

### Timeline Features

- Zoom in/out to adjust time scale
- Filter by project
- Click items to view details
- Visual indicators for overdue items

## Performance

The performance page tracks team KPI metrics.

### KPI Score Calculation

KPI scores are calculated from:
- **Workload (20%):** Active task load balance
- **Velocity (25%):** Tasks completed in last 30 days
- **Cycle Time (20%):** Average time to complete tasks
- **On-Time (20%):** Tasks completed by due date
- **Defect Rate (15%):** Bugs re-opened

### Viewing Performance

- **Team Overview:** Average KPI across team
- **Individual Performance:** Each member's KPI score
- **Trends:** Performance over time
- **Needs Attention:** Members with KPI < 70

### Performance Categories

- **80-100:** Good performance
- **60-79:** Fair performance
- **Below 60:** At risk

## Schedule

The schedule is a personal calendar for events and meetings.

### Creating an Event

1. Navigate to the Schedule page
2. Click on a date or "New Event"
3. Fill in:
   - Title
   - Description
   - Start date/time
   - End date/time
   - Location
   - Attendees
4. Click "Create Event"

### Calendar Views

- **Month View:** Full month overview
- **Week View:** Weekly schedule
- **Day View:** Detailed daily agenda

### Knowledge Sessions

Schedule knowledge sharing sessions with:
- Title and description
- Date and time
- Attendees
- Visibility (who can see)
- Reminder settings

## Team

View team members and their workload.

### Team Overview

- List of all team members
- Current task assignments
- Workload status
- KPI scores

### Member Details

Click a member to see:
- Assigned tasks
- Recent activity
- Performance history
- Contact information

## Updates

Share daily or weekly standup updates.

### Creating an Update

1. Navigate to the Updates page
2. Click "New Update"
3. Select type (Daily or Weekly)
4. Fill in:
   - Pending Tasks
   - Completed Tasks
   - Blockers
   - Notes
5. Click "Post Update"

### Activity Feed

- View all team updates
- Filter by author or date
- Edit your own updates
- Reply to updates (coming soon)

## Board

The Team Weekly Board for collaborative planning.

### Creating a Weekly Post

1. Navigate to the Board page
2. Click "New Post"
3. Select week
4. Write content in Markdown
5. Click "Post"

### Board Features

- Week navigation
- AI summaries of posts
- Append to existing posts
- Markdown support

## AI Assistant

TeamFlow AI helps with task management and planning.

### AI Features

**Task Input:**
- Natural language task creation
- Automatic field extraction
- Smart suggestions

**Task Breakdown:**
- Describe a feature
- AI suggests subtasks
- Adjust and confirm

**Project Summary:**
- Get AI-generated project status
- Summarize progress
- Identify risks

### Using AI Assistant

1. Click the AI chat icon
2. Type your request
3. AI responds with suggestions
4. Apply suggestions as needed

## Role-Specific Features

### Members

- View and update assigned tasks
- Post standup updates
- View personal schedule
- See team activity feed

### Supervisors

- All member features plus:
- Team health dashboard
- KPI monitoring
- Assign tasks to team members
- View all team updates

### Assistant Managers

- All supervisor features for their scope

### Managers

- All features across all teams
- Organization-wide visibility
- Cross-team analytics

## Tips and Best Practices

### Task Management

- Break large tasks into smaller subtasks
- Set realistic due dates
- Update status regularly
- Use tags for categorization
- Assign clear priorities

### Team Collaboration

- Post daily standup updates
- Keep task descriptions clear
- Communicate blockers early
- Use @mentions for attention (coming soon)
- Review team performance regularly

### Project Planning

- Use milestones for major deliverables
- Link tasks to milestones
- Review timeline regularly
- Adjust plans based on progress
- Document decisions in milestones

## Getting Help

### Common Issues

**Can't see a task:**
- Check if you're assigned to it
- Verify project visibility
- Contact your supervisor

**KPI score seems wrong:**
- Allow 24 hours for recalculation
- Check task completion dates
- Verify no data entry errors

**Can't assign task:**
- Check if user is in your visible scope
- Verify user exists in your sub-team
- Contact manager for cross-team assignments

### Support

For issues or questions:
- Contact your team supervisor
- Check with your manager for access issues
- Report bugs to the development team
