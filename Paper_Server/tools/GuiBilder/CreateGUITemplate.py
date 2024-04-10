import yaml

# Define the header information
header_info = """
open_command: skilltree_scout
size: 54
menu_title: 'Scout Skill Tree %sapi_default_currentavailableskillpoints%'
open_requirement:
  requirements:
    permission:
      type: has permission
      permission: deluxemenus.admin
      deny_commands:
        - '[message] &cYou don''t have permission to do that!'
items:"""

# Example mappings from icon names to Minecraft materials. Adjust these as needed.
icon_to_material = {
    'attr_ld.png': 'GOLD_INGOT:128000',
    'attr_lr.png': 'GOLD_INGOT:128001',
    'attr_lrd.png': 'GOLD_INGOT:128002',
    'attr_lt.png': 'GOLD_INGOT:128003',
    'attr_ltd.png': 'GOLD_INGOT:128004',
    'attr_ltr.png': 'GOLD_INGOT:128005',
    'attr_ltrd.png': 'GOLD_INGOT:128006',
    'attr_rd.png': 'GOLD_INGOT:128007',
    'attr_td.png': 'GOLD_INGOT:128008',
    'attr_tr.png': 'GOLD_INGOT:128009',
    'attr_trd.png': 'GOLD_INGOT:128010',
    'node_d.png': 'GOLD_INGOT:128011',
    'node_l.png': 'GOLD_INGOT:128012',
    'node_ld.png': 'GOLD_INGOT:128013',
    'node_lr.png': 'GOLD_INGOT:128014',
    'node_lrd.png': 'GOLD_INGOT:128015',
    'node_lt.png': 'GOLD_INGOT:128016',
    'node_ltd.png': 'GOLD_INGOT:128017',
    'node_ltr.png': 'GOLD_INGOT:128018',
    'node_ltrd.png': 'GOLD_INGOT:128019',
    'node_r.png': 'GOLD_INGOT:128020',
    'node_rd.png': 'GOLD_INGOT:128021',
    'node_t.png': 'GOLD_INGOT:128022',
    'node_td.png': 'GOLD_INGOT:128023',
    'node_tr.png': 'GOLD_INGOT:128024',
    'node_trd.png': 'GOLD_INGOT:128025',
    'skill_d.png': 'GOLD_INGOT:128026',
    'skill_l.png': 'GOLD_INGOT:128027',
    'skill_lr.png': 'GOLD_INGOT:128028',
    'skill_lrd.png': 'GOLD_INGOT:128029',
    'skill_lt.png': 'GOLD_INGOT:128030',
    'skill_ltd.png': 'GOLD_INGOT:128031',
    'skill_ltr.png': 'GOLD_INGOT:128032',
    'skill_ltrd.png': 'GOLD_INGOT:128033',
    'skill_r.png': 'GOLD_INGOT:128034',
    'skill_rd.png': 'GOLD_INGOT:128035',
    'skill_t.png': 'GOLD_INGOT:128036',
    'skill_td.png': 'GOLD_INGOT:128037',
    'skill_tr.png': 'GOLD_INGOT:128038',
    'skill_trd.png': 'GOLD_INGOT:128039'
}


unique_skill_names = set()

def calculate_slot_number(slot_id):
    """
    Calculate the Minecraft inventory slot number based on the row and column.
    Minecraft inventory rows and columns start at 0 and go to 5 for rows (6 total)
    and 0 to 8 for columns (9 total), making up a grid of 54 slots.
    """
    # Extract row and column from slot_id, assuming format 'row_column'
    row, column = map(int, slot_id.split('_'))
    # Calculate the slot number
    return row * 9 + column

def convert_slot_to_template(slot_id, slot_info):
    global unique_skill_names  # Use the global set to track skill names

    # Calculate the actual slot based on row and column
    actual_slot = calculate_slot_number(slot_id)

    # Extract and prepare skill name
    skill_name = slot_info['name']
    # Add the skill name to the set of unique skill names
    unique_skill_names.add(skill_name)
    icon_material = icon_to_material.get(slot_info['icon'], 'STONE')  # Default to STONE if icon not found
    material, model_data = icon_material.split(':') if ':' in icon_material else (
    icon_material, '0')  # Default model_data to '0'

    complete_material = 'LEATHER'  # Default material for the complete state
    display_name = skill_name.replace('_', ' ').title()
    lore = "Customize this lore based on the slot's details"

    # Generate dynamic click commands based on placeholders
    dynamic_click_commands = ""
    if slot_info['type'] != 'skill':
        for placeholder, value in slot_info.get('placeholders', {}).items():
            dynamic_click_commands += f"\n    - '[console] class forceattr %player_name% {placeholder} {value}'"

    if slot_info['type'] == 'skill':
        dynamic_click_commands += f"\n    - '[console] class forceskill %player_name% up {slot_info['details']}'"
        pass

    click_commands = f"""
      - '[message] &6&lSkill&eTree &8> &7You have unlocked &a{display_name}'
    - '[console] lp user %player_name% permission set skilltree.{skill_name} true'{dynamic_click_commands}
    - '[console] class forcepoints add %player_name% -1'
    """.strip()
    actual_slot = calculate_slot_number(slot_id)
    # Dynamic requirements generation
    requirements_list = slot_info.get('requirements', [])
    dynamic_requirements = ""
    for index, req in enumerate(requirements_list, start=1):
        dynamic_requirements += f"""\n      req{index}:
        type: has permission
        permission: skilltree.{req}
        optional: true"""

    base_requirements = f"""
        money:
        type: '>='
        input: '%sapi_default_currentavailableskillpoints%'
        output: '1'
        optional: false
        deny_commands:
          - '[message] &6&lSkill&eTree &8» &7You don''t have enough Skill Points!'
    """.strip()

    requirements = f"""requirements:\n      {base_requirements}{dynamic_requirements}"""


    # Adjust the minimum requirements count based on the actual number of requirements
    minimum_requirements = len(requirements_list)  # Adding 1 for the money requirement

    slot_template = f"""
'slot_{actual_slot}':
  material: {material}
  model_data: {model_data}
  data: 1
  slot: {actual_slot}
  priority: 20
  display_name: "&a{display_name}"
  lore:
    - "{lore}"
  click_requirement:
    minimum_requirements: 2
    stop_at_success: true
    {requirements}
  click_commands:
    {click_commands}
'slot_{actual_slot}_complete':
  material: {complete_material}
  data: 1
  slot: {actual_slot}
  priority: 10
  display_name: "&aComplete: {display_name}"
  lore:
    - "&aAllocated"
    - "{lore}"
  view_requirement:
    requirements:
      permission:
        type: has permission
        permission: skilltree.{skill_name}
""".strip()
    return slot_template

with open('script_inputs/final.yaml', 'r') as file:
    slots_data = yaml.safe_load(file)

# Initialize the full configuration with the header information
full_configuration = header_info

# Process each slot and add to the full configuration
for slot_id, slot_info in slots_data['slots'].items():
    full_configuration += '\n  ' + convert_slot_to_template(slot_id, slot_info).replace("\n", "\n  ")

# Save the full configuration to 'gui.yml'
with open('script_outputs/gui.yml', 'w') as file:
    file.write(full_configuration)

print("Configuration saved to gui.yml")

with open('script_outputs/permissions_list.txt', 'w') as perm_file:
    for skill_name in sorted(unique_skill_names):
        # Write each unique skill name, prefixed with 'skilltree.' to indicate the permission
        perm_file.write(f"skilltree.{skill_name}\n")
print("Configuration saved to gui.yml")
print("Permissions list saved to permissions_list.txt")