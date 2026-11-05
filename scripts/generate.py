import gzip
import os
import urllib.request
import xml.etree.ElementTree as ET

def generate_merged_epg():
    sources_env = os.environ.get('EPG_SOURCES', '')
    sources = [s.strip() for s in sources_env.replace(',', '\n').splitlines() if s.strip()]

    if not sources:
        print("No EPG sources found in environment variables.")
        return

    output_path = 'AIO_epg.xml.gz'

    combined_root = ET.Element('tv')
    channel_ids = set()
    channel_count = 0
    programme_count = 0

    for idx, source in enumerate(sources):
        temp_file = f"temp_{idx}.xml.gz"
        print(f"Fetching source #{idx + 1}...")
        try:
            urllib.request.urlretrieve(source, temp_file)
            
            with gzip.open(temp_file, 'rb') as f_in:
                tree = ET.parse(f_in)
                root = tree.getroot()

                for child in root:
                    if child.tag == 'channel':
                        ch_id = child.get('id')
                        if ch_id not in channel_ids:
                            channel_ids.add(ch_id)
                            combined_root.append(child)
                            channel_count += 1
                    elif child.tag == 'programme':
                        combined_root.append(child)
                        programme_count += 1

        except Exception as e:
            print(f"Error processing source #{idx + 1}: {e}")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    print(f"Writing {channel_count} channels and {programme_count} programmes to {output_path}...")
    combined_tree = ET.ElementTree(combined_root)
    
    with gzip.open(output_path, 'wb') as f_out:
        combined_tree.write(f_out, encoding='utf-8', xml_declaration=True)

    print("EPG generation completed successfully!")

if __name__ == "__main__":
    generate_merged_epg()
