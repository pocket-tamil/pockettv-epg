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

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_path = os.path.join(root_dir, 'AIO_epg.xml.gz')

    combined_root = ET.Element('tv')
    channel_ids = set()
    total_channels = 0
    total_programmes = 0

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for idx, source in enumerate(sources):
        temp_file = f"temp_{idx}.xml.gz"
        print(f"\n--- Processing Source #{idx + 1}: {source} ---")
        try:
            req = urllib.request.Request(source, headers=headers)
            with urllib.request.urlopen(req) as response, open(temp_file, 'wb') as out_file:
                out_file.write(response.read())
            
            with gzip.open(temp_file, 'rb') as f_in:
                tree = ET.parse(f_in)
                root = tree.getroot()

                source_channels = 0
                source_programmes = 0

                # Recursive helper or deep search for elements regardless of nesting
                for elem in root.iter():
                    if elem.tag == 'channel':
                        ch_id = elem.get('id')
                        if ch_id and ch_id not in channel_ids:
                            channel_ids.add(ch_id)
                            combined_root.append(elem)
                            source_channels += 1
                            total_channels += 1
                    elif elem.tag == 'programme':
                        combined_root.append(elem)
                        source_programmes += 1
                        total_programmes += 1

                print(f"Extracted {source_channels} channels and {source_programmes} programmes from Source #{idx + 1}.")

        except Exception as e:
            print(f"Error processing source #{idx + 1}: {e}")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    print(f"\nTotal combined: {total_channels} channels and {total_programmes} programmes.")
    print(f"Writing final compressed data to {output_path}...")
    
    combined_tree = ET.ElementTree(combined_root)
    with gzip.open(output_path, 'wb') as f_out:
        combined_tree.write(f_out, encoding='utf-8', xml_declaration=True)

    print("EPG generation completed successfully!")

if __name__ == "__main__":
    generate_merged_epg()
