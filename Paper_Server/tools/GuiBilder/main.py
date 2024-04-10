import os
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
                             QListWidget, QGridLayout, QTextEdit, QListWidgetItem, QFormLayout, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
import yaml

menu_data = {
    'slots': {}
}


class SkillApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_slot = None
        self.current_button = None
        self.initUI()
        self.placeholdersInputs = {}

    def initUI(self):
        self.setGeometry(100, 100, 875 , 900)
        self.setWindowTitle('Skill Configuration App')

        # Main layout is horizontal
        mainLayout = QHBoxLayout(self)

        # Layout for grid, details and third dynamic element, stacked vertically
        gridDetailLayout = QVBoxLayout()

        # Save button at the top of the gridDetailLayout
        self.saveButton = QPushButton('Save Configuration')
        self.saveButton.clicked.connect(self.saveConfiguration)
        gridDetailLayout.addWidget(self.saveButton)

        # Grid layout for buttons
        self.gridLayout = QGridLayout()
        self.gridLayout.setHorizontalSpacing(2)
        self.gridLayout.setVerticalSpacing(2)
        gridDetailLayout.addLayout(self.gridLayout)

        # Create form layout for the details
        self.detailsForm = QFormLayout()
        gridDetailLayout.addLayout(self.detailsForm)
        # Horizontal divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        gridDetailLayout.addWidget(divider)

        # Third dynamic element layout
        self.thirdDynamicElement = QVBoxLayout()
        gridDetailLayout.addLayout(self.thirdDynamicElement)

        # Add the gridDetailLayout to the main layout
        mainLayout.addLayout(gridDetailLayout)

        # Second dynamic element layout, placed on the right
        self.dynamicElement = QVBoxLayout()
        mainLayout.addLayout(self.dynamicElement)

        # Call the creation methods
        self.createSkillGrid()
        self.createDetailsForm()

        self.setLayout(mainLayout)

    def createSkillGrid(self):
        for row in range(6):
            for col in range(9):
                button = QPushButton()
                button.setFixedSize(64, 64)
                button.setObjectName(f'button_{row}_{col}')
                button.clicked.connect(self.onSkillButtonClick)
                self.gridLayout.addWidget(button, row, col)
    def createSkillRequirementsDropdowns(self):
        self.skillRequirementsCombos = [QComboBox() for _ in range(4)]
        for i, comboBox in enumerate(self.skillRequirementsCombos, start=1):
            comboBox.addItem("")  # Add a blank item
            self.detailsForm.addRow(QLabel(f'Skill Requirement {i}:'), comboBox)
        # Populate the first dropdown with 'start_ability'
        self.skillRequirementsCombos[0].addItem("start_ability")
        self.updateSkillRequirementsDropdowns()

    def updateSkillRequirementsDropdowns(self):
        skill_names = [slot_info['name'] for slot_info in menu_data['slots'].values() if 'name' in slot_info]
        for comboBox in self.skillRequirementsCombos:
            currentText = comboBox.currentText()
            comboBox.clear()
            comboBox.addItem("")  # Add a blank item
            comboBox.addItem("start_ability")  # Add 'start_ability' to all dropdowns
            comboBox.addItems(skill_names)
            if currentText in skill_names:  # Restore previously selected item if it still exists
                comboBox.setCurrentText(currentText)
    def createDetailsForm(self):
        self.skillNameEdit = QLineEdit()
        self.detailsForm.addRow(QLabel('Name of Skill:'), self.skillNameEdit)

        self.skillTypeCombo = QComboBox()
        self.skillTypeCombo.addItem("")  # Add an empty string as the first item for default
        self.skillTypeCombo.addItems(['attr', 'node', 'skill'])
        self.skillTypeCombo.setCurrentIndex(0)  # Set the first item (empty string) as selected
        self.skillTypeCombo.currentIndexChanged.connect(self.onSkillTypeChange)
        self.detailsForm.addWidget(QLabel('Skill Type:'))
        self.detailsForm.addWidget(self.skillTypeCombo)

        self.iconSelectorCombo = QComboBox()
        self.iconSelectorCombo.currentIndexChanged.connect(self.updateButtonIcons)
        self.detailsForm.addRow(QLabel('Icon Selector:'), self.iconSelectorCombo)
        self.skillRequirementsCombos = [QComboBox() for _ in range(4)]
        self.createSkillRequirementsDropdowns()
    def clearThirdDynamicElement(self):
        # Clear any existing widgets in the third dynamic element layout
        while self.thirdDynamicElement.count():
            child = self.thirdDynamicElement.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.placeholdersInputs.clear()

    def onSkillButtonClick(self):
        self.setSlotButtonsEnabled(False)
        try:
            if self.current_slot is not None:
                self.saveCurrentConfiguration()
                self.clearThirdDynamicElement()

            self.current_button = self.sender()
            self.current_slot = self.current_button.objectName().split('button_')[-1]

            slot_data = menu_data['slots'].get(self.current_slot, {})
            self.skillNameEdit.setText(slot_data.get('name', ''))
            self.loadSkillRequirements()
            skill_type = slot_data.get('type', '')
            if skill_type:
                index = self.skillTypeCombo.findText(skill_type)
                self.skillTypeCombo.setCurrentIndex(index)
            else:
                self.skillTypeCombo.setCurrentIndex(0)  # Set to blank if no skill type

            icon = slot_data.get('icon', '')
            if icon:
                self.updateIconSelector(skill_type)
                self.iconSelectorCombo.setCurrentText(icon)
            else:
                # Update the icon selector with a default icon if there's no specific icon set
                self.updateIconSelector('default')  # Assuming 'default' is a valid skill_type for icons
                self.iconSelectorCombo.setCurrentText('default_icon.png')
            self.updateSkillRequirementsDropdowns()
            self.updateDynamicElement(skill_type)

        finally:
            self.setSlotButtonsEnabled(True)
    def loadSkillRequirements(self):
        # Load the skill requirements if they exist
        requirements = menu_data['slots'].get(self.current_slot, {}).get('requirements', [""] * 4)
        for comboBox, requirement in zip(self.skillRequirementsCombos, requirements):
            comboBox.setCurrentText(requirement or "")
    def setSlotButtonsEnabled(self, enabled):
        for row in range(6):
            for col in range(9):
                button = self.gridLayout.itemAtPosition(row, col).widget()
                if button:
                    button.setEnabled(enabled)
    def updateIconSelector(self, skill_type):
        self.iconSelectorCombo.clear()  # Clear current items.
        iconsPath = os.path.join('icons', skill_type)  # Construct the path based on skill type.
        if os.path.exists(iconsPath):
            icons = [f for f in os.listdir(iconsPath) if os.path.isfile(os.path.join(iconsPath, f))]
            self.iconSelectorCombo.addItems(icons)  # Populate the icon selector.
        else:
            print(f"No icons found in {iconsPath}")

    def updateButtonIcons(self):
        if not self.current_button or not self.iconSelectorCombo.currentText():
            return
        icon_name = self.iconSelectorCombo.currentText()
        skill_type = self.skillTypeCombo.currentText()
        icon_path = os.path.join('icons', skill_type, icon_name)
        if os.path.exists(icon_path):
            self.current_button.setIcon(QIcon(icon_path))
            self.current_button.setIconSize(QSize(64, 64))

    def onSkillTypeChange(self, index):
        # Ensure this method updates the icon selector based on the selected skill type.
        skill_type = self.skillTypeCombo.currentText()
        self.updateIconSelector(skill_type)  # This should trigger icon selector update.
        self.updateDynamicElement(skill_type)  # Continue with dynamic element updates.

    def updateDynamicElement(self, skill_type):
        # Clear any existing widgets in the second dynamic element layout
        for i in reversed(range(self.dynamicElement.count())):
            widget = self.dynamicElement.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Clear the third dynamic element as well
        self.clearThirdDynamicElement()

        if skill_type == 'skill':
            # If 'skill', add a text box to the second dynamic element
            textBox = QTextEdit()
            textBox.setPlaceholderText("Enter skill details")
            self.dynamicElement.addWidget(textBox)
            # Load saved details if they exist
            if 'details' in menu_data['slots'].get(self.current_slot, {}):
                textBox.setText(menu_data['slots'][self.current_slot]['details'])
        elif skill_type in ['attr', 'node']:
            # If 'attr' or 'node', add a list widget to the second dynamic element
            self.listWidget = QListWidget()
            self.listWidget.setSelectionMode(QListWidget.MultiSelection)
            self.dynamicElement.addWidget(self.listWidget)

            # Populate the list widget and check off any saved selections
            placeholders_file = f'script_inputs/{skill_type}_placeholder_list.txt'
            if os.path.exists(placeholders_file):
                with open(placeholders_file, 'r') as file:
                    for line in file:
                        item = QListWidgetItem(line.strip())
                        self.listWidget.addItem(item)
                        # Check off the item if it was previously selected
                        if line.strip() in menu_data['slots'].get(self.current_slot, {}).get('selections', []):
                            item.setSelected(True)

            # Connect the selection change signal to create input boxes for selections
            self.listWidget.itemSelectionChanged.connect(self.createInputBoxesForSelections)

            # Create input boxes for any saved selections
            self.createInputBoxesForSelections()

    def createInputBoxesForSelections(self):
        # Clear any existing widgets in the third dynamic element layout first
        for i in reversed(range(self.thirdDynamicElement.count())):
            widget = self.thirdDynamicElement.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Clear the dictionary that tracks the input boxes
        self.placeholdersInputs.clear()

        # Create new QLineEdit for each selected item in the second dynamic element's QListWidget
        selectedItems = self.listWidget.selectedItems()
        for item in selectedItems:
            label = QLabel(f"Value for {item.text()}:")
            inputBox = QLineEdit()
            inputBox.setObjectName(f"input_{item.text()}")  # Set object name to match the placeholder

            # If we have saved values, set them
            if item.text() in menu_data['slots'].get(self.current_slot, {}).get('placeholders', {}):
                inputBox.setText(menu_data['slots'][self.current_slot]['placeholders'][item.text()])

            # Store the input box reference in the dictionary
            self.placeholdersInputs[item.text()] = inputBox

            # Add the label and input box to the layout
            self.thirdDynamicElement.addWidget(label)
            self.thirdDynamicElement.addWidget(inputBox)

    def saveCurrentConfiguration(self):
        if self.current_slot:
            slot_info = menu_data['slots'].get(self.current_slot, {})
            slot_info['name'] = self.skillNameEdit.text()
            slot_info['type'] = self.skillTypeCombo.currentText()
            slot_info['icon'] = self.iconSelectorCombo.currentText()
            slot_info['requirements'] = [combo.currentText() for combo in self.skillRequirementsCombos if
                                         combo.currentText()]
            if self.skillTypeCombo.currentText() in ['attr', 'node']:
                # Save selections from the second element
                listWidget = self.findChild(QListWidget)
                selections = [item.text() for item in listWidget.selectedItems()]
                slot_info['selections'] = selections

                # Save input values from the third element
                placeholder_values = {}
                for placeholder, inputBox in self.placeholdersInputs.items():
                    placeholder_values[placeholder] = inputBox.text()
                slot_info['placeholders'] = placeholder_values

            elif self.skillTypeCombo.currentText() == 'skill':
                # Save details for 'skill' type
                textBox = self.findChild(QTextEdit)
                slot_info['details'] = textBox.toPlainText() if textBox else ""

            # Update the slot info
            menu_data['slots'][self.current_slot] = slot_info

            # Save to file every time for now (consider optimizing this)
            with open('script_inputs/configuration.yaml', 'w') as file:
                yaml.dump(menu_data, file, default_flow_style=False)

    def saveConfiguration(self):
        # Save the current configurations before saving final configurations
        self.saveCurrentConfiguration()

        # Write to final.yaml only when the 'Save Configuration' button is clicked
        with open('script_inputs/final.yaml', 'w') as file:
            yaml.dump(menu_data, file, default_flow_style=False)

        # You may want to provide feedback that the configurations were saved
        print("Final configuration saved to final.yaml.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SkillApp()
    ex.show()
    sys.exit(app.exec_())
