def organize_attributes_by_comments(file_path):
    categories = {"MAIN ATTRIBUTES": [], "OTHER ATTRIBUTES": []}
    current_category = None

    with open(file_path, "r") as file:
        lines = file.readlines()

    # Iterate through each line to process categories and attributes
    for line in lines:
        if "########" in line:  # Check for a new category
            current_category = "MAIN ATTRIBUTES" if "MAIN ATTRIBUTES" in line else "OTHER ATTRIBUTES"
        elif not line.startswith(" ") and ":" in line:  # Top-level attribute
            attribute_name = line.split(":")[0].strip()
            if current_category:  # Ensure a category has been identified
                categories[current_category].append(attribute_name)

    # Writing organized attributes to their respective files
    with open("script_inputs/attr_placeholder_list.txt", "w") as attr_file:
        for attribute in categories["MAIN ATTRIBUTES"]:
            attr_file.write(f"{attribute}\n")

    with open("script_inputs/node_placeholder_list.txt", "w") as node_file:
        for attribute in categories["OTHER ATTRIBUTES"]:
            if attribute not in categories["MAIN ATTRIBUTES"]:  # Exclude main attributes
                node_file.write(f"{attribute}\n")

    return "script_inputs/attr_placeholder_list.txt", "script_inputs/node_placeholder_list.txt"

# Assuming 'attributes.yml' is the path to your YAML file
attributes_yml_path = "script_inputs/attributes.yml"
# Call the function to organize attributes based on comments
organize_attributes_by_comments(attributes_yml_path)
