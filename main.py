import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from io import StringIO


def convert_color_values(input_xml: str):
    '''Parse xml data and convert separate r g b a values to single hex value. Also change "Skinmanager" element to "Theme"'''
    root = ET.fromstring(input_xml)

    for element in root.iter():
        if len(element) == 4 and all(child.tag in {'R', 'G', 'B', 'Alpha'} for child in element):
            r = int(element.find('R').get('Value'))
            g = int(element.find('G').get('Value'))
            b = int(element.find('B').get('Value'))
            a = int(element.find('Alpha').get('Value'))
            
            hex_value = f'#{r:02x}{g:02x}{b:02x}{a:02x}'
            element.set("Value",hex_value)
            
            # Remove r, g, b, a seb-elements
            element.remove(element.find('R'))
            element.remove(element.find('G'))
            element.remove(element.find('B'))
            element.remove(element.find('Alpha'))

            # Remove text content
            element.text = ""

        # Change "SkinManager" element to "Theme"
        if element.tag == "SkinManager":
            print(f'Changing element tag from "SkinManager" to "Theme"')
            element.tag = "Theme"

    # Return the converted XML data
    return ET.tostring(root, encoding='unicode',short_empty_elements=True,xml_declaration=False)


def strip_xml(data: str):
    '''Strips the first line (XML declaration) from the given input data'''
    return "\n".join(data.splitlines()[1:]) if data.startswith('<?xml') else data


def save_to_file(data, filename):
    with open(filename, 'w') as file:
        file.write(data)

def read_from_file(filename):
    '''Reads inputfile and strips XML declaration'''
    with open(filename, 'r') as file:
        return strip_xml(file.read())


def merge_missing(input_data, reference_data):
    '''Merge missing elements from reference_data into input_data at the correct position'''
    input_root = ET.fromstring(input_data)
    reference_root = ET.fromstring(reference_data)

    print("Setting Version")
    input_root.attrib["MinorVersion"] = reference_root.attrib["MinorVersion"]


    input_tags = [element.tag for element in input_root[0]]
    reference_tags = [element.tag for element in reference_root[0]]


    for reference_element in reference_root[0]:
        print(f'Checking reference element: {reference_element.tag}')
        print(" Reference Element Index: ", reference_tags.index(reference_element.tag))

        try: 
            print(" Index in input data: ", input_tags.index(reference_element.tag))
        except Exception as e: 
            print("Not found - inserting element")
            input_root[0].insert(reference_tags.index(reference_element.tag), reference_element)
        else:
            print("Item already exists")

        print("--------------------")

    return input_root



'''
This script is made to convert old Ableton Live 10 Theme files to the new format used in Ableton Live 12.

The reference file HAS TO BE one of the current default themes in Ableton Live 12.
So depending on if the input theme is light or dark, the reference file should be 
either "Default Light Neutral Medium.ask" or "Default Dark Neutral Medium.ask", to avoid unreadable text, etc.
(Or any of the other default themes in Ableton Live 12)
'''


# Define input/reference files
input_file = 'fire.ask'
reference_file = 'Default Dark Neutral Medium.ask'



# Define output filename
output_filename = input_file.split('.')[0] + '_converted.ask' if input_file[-4:] == '.ask' else 'converted.ask'



# Get data from input file
input_data = read_from_file(input_file)

# Get data from reference file
reference_data = read_from_file(reference_file)


# Format input data
formatted_input = strip_xml(input_data)

# Format reference data
formatted_reference = strip_xml(reference_data)



# Convert input data values
converted_input_data = convert_color_values(formatted_input.strip())


# Merge missing elements
merged = merge_missing(converted_input_data,formatted_reference)




ET.ElementTree(merged).write(output_filename, encoding='UTF8', short_empty_elements=True, xml_declaration=True)

print(f'Converted data has been saved to {output_filename}')



# Save output
#save_to_file(converted_input_data, output_filename)


#print(f'Converted data has been saved to {output_filename}')
