import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Zerve design system colors
bg_color = '#1D1D20'
text_primary = '#fbfbff'
text_secondary = '#909094'
color_primary = '#A1C9F4'
color_accent = '#FFB482'
color_success = '#8DE5A1'
color_warning = '#FF9F9B'
color_info = '#D0BBFF'

# Create figure with dark background
fig, ax = plt.subplots(figsize=(18, 12))
fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

# Entity definitions with positions
entities = {
    'Organizations': {'pos': (2, 10), 'color': color_primary, 'fields': ['organization_id (PK)', 'name', 'slug', 'tier', 'status']},
    'Users': {'pos': (2, 8), 'color': color_accent, 'fields': ['user_id (PK)', 'organization_id (FK)', 'email', 'role', 'status']},
    'Projects': {'pos': (6, 9), 'color': color_success, 'fields': ['project_id (PK)', 'organization_id (FK)', 'created_by (FK)', 'name', 'status']},
    'Tasks': {'pos': (10, 9), 'color': color_warning, 'fields': ['task_id (PK)', 'organization_id (FK)', 'project_id (FK)', 'assigned_to (FK)', 'title', 'status']},
    'Subtasks': {'pos': (14, 9), 'color': color_info, 'fields': ['subtask_id (PK)', 'organization_id (FK)', 'task_id (FK)', 'title', 'status']},
    'Activities': {'pos': (6, 6), 'color': '#1F77B4', 'fields': ['activity_id (PK)', 'organization_id (FK)', 'user_id (FK)', 'entity_type', 'action']},
    'Notifications': {'pos': (10, 6), 'color': '#9467BD', 'fields': ['notification_id (PK)', 'organization_id (FK)', 'user_id (FK)', 'entity_type', 'is_read']},
    'Comments': {'pos': (14, 6), 'color': '#8C564B', 'fields': ['comment_id (PK)', 'organization_id (FK)', 'user_id (FK)', 'entity_type', 'content']},
    'Project Members': {'pos': (6, 3), 'color': '#E377C2', 'fields': ['project_member_id (PK)', 'organization_id (FK)', 'project_id (FK)', 'user_id (FK)']},
    'Attachments': {'pos': (10, 3), 'color': '#C49C94', 'fields': ['attachment_id (PK)', 'organization_id (FK)', 'entity_type', 'entity_id']},
}

# Draw entity boxes
box_width = 3
box_height = 1.5

for entity_name, entity_info in entities.items():
    x, y = entity_info['pos']
    color = entity_info['color']
    
    # Draw box
    box = FancyBboxPatch((x - box_width/2, y - box_height/2), box_width, box_height,
                          boxstyle="round,pad=0.05", 
                          edgecolor=color, facecolor=bg_color, 
                          linewidth=2.5, zorder=2)
    ax.add_patch(box)
    
    # Entity name
    ax.text(x, y + 0.5, entity_name, 
            ha='center', va='center', 
            fontsize=11, fontweight='bold', 
            color=color, zorder=3)
    
    # Fields (show first 3)
    fields_text = '\n'.join(entity_info['fields'][:3])
    if len(entity_info['fields']) > 3:
        fields_text += f'\n+ {len(entity_info["fields"]) - 3} more...'
    
    ax.text(x, y - 0.2, fields_text, 
            ha='center', va='center', 
            fontsize=7, color=text_secondary, zorder=3)

# Define relationships with arrows
relationships = [
    # From Organizations
    ('Organizations', 'Users', 'CASCADE'),
    ('Organizations', 'Projects', 'CASCADE'),
    ('Organizations', 'Tasks', 'CASCADE'),
    
    # From Users
    ('Users', 'Projects', 'RESTRICT\n(created_by)'),
    ('Users', 'Tasks', 'RESTRICT\n(created_by)'),
    
    # From Projects
    ('Projects', 'Tasks', 'CASCADE'),
    ('Projects', 'Project Members', 'CASCADE'),
    
    # From Tasks
    ('Tasks', 'Subtasks', 'CASCADE'),
    ('Tasks', 'Tasks', 'CASCADE\n(parent)'),
    
    # Activities, Notifications, Comments
    ('Users', 'Activities', 'CASCADE'),
    ('Users', 'Notifications', 'CASCADE'),
    ('Users', 'Comments', 'CASCADE'),
]

# Draw arrows for relationships
for source, target, label in relationships:
    if source in entities and target in entities:
        x1, y1 = entities[source]['pos']
        x2, y2 = entities[target]['pos']
        
        # Self-reference for Tasks
        if source == target:
            # Draw curved arrow for self-reference
            arc = mpatches.FancyArrowPatch((x1 + box_width/2, y1),
                                          (x1 + box_width/2, y1 - 0.5),
                                          connectionstyle="arc3,rad=.5",
                                          arrowstyle='->', 
                                          linewidth=1.5, 
                                          color=text_secondary,
                                          alpha=0.6, zorder=1)
            ax.add_patch(arc)
            ax.text(x1 + box_width/2 + 0.5, y1 - 0.25, label,
                   fontsize=6, color=text_secondary, ha='left')
        else:
            # Calculate arrow positions (from edge to edge)
            dx = x2 - x1
            dy = y2 - y1
            dist = np.sqrt(dx**2 + dy**2)
            
            if dist > 0:
                # Offset from center to edge
                offset_x1 = (dx / dist) * (box_width / 2)
                offset_y1 = (dy / dist) * (box_height / 2)
                offset_x2 = -(dx / dist) * (box_width / 2)
                offset_y2 = -(dy / dist) * (box_height / 2)
                
                arrow = FancyArrowPatch((x1 + offset_x1, y1 + offset_y1),
                                       (x2 + offset_x2, y2 + offset_y2),
                                       arrowstyle='->', 
                                       linewidth=1.5, 
                                       color=text_secondary,
                                       alpha=0.6, zorder=1)
                ax.add_patch(arrow)
                
                # Label near midpoint
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                ax.text(mid_x, mid_y, label,
                       fontsize=6, color=text_secondary,
                       bbox=dict(boxstyle='round,pad=0.3', facecolor=bg_color, edgecolor='none', alpha=0.8))

# Title and legend
ax.text(8, 11.5, 'PostgreSQL Multi-Tenant Schema - Entity Relationship Diagram',
        fontsize=18, fontweight='bold', color=text_primary, ha='center')

ax.text(8, 11, 'Organization-based tenant isolation with Row-Level Security (RLS)',
        fontsize=11, color=text_secondary, ha='center', style='italic')

# Legend
legend_items = [
    '• All tables include organization_id for tenant isolation',
    '• Indexes on (organization_id, resource_id) for performance',
    '• CASCADE: Delete dependent records | RESTRICT: Preserve audit trail',
    '• RLS policies enforce tenant boundaries at database level',
]

legend_y = 0.5
for i, item in enumerate(legend_items):
    ax.text(1, legend_y - i*0.3, item,
           fontsize=9, color=text_secondary, va='top')

# Key features box
features_text = """KEY FEATURES:
• UUID primary keys
• Soft deletes (deleted_at)
• Automatic timestamps
• JSONB for flexibility
• Array types (tags, mentions)
• Partial indexes
• Audit trail (activities)"""

ax.text(15, 1, features_text,
       fontsize=8, color=text_primary,
       bbox=dict(boxstyle='round,pad=0.5', facecolor=bg_color, 
                edgecolor=color_primary, linewidth=2),
       va='top', ha='left')

# Set axis properties
ax.set_xlim(-1, 18)
ax.set_ylim(-1, 12)
ax.axis('off')

plt.tight_layout()
plt.savefig('multi_tenant_erd.png', dpi=300, facecolor=bg_color, bbox_inches='tight')
print("✅ Entity Relationship Diagram created: multi_tenant_erd.png")
plt.show()
