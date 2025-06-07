from PyPDF2 import PdfReader, PdfWriter
import re
from rapidfuzz import fuzz

#TODO Add OCR
#Testing Data
# name = "pdf-bookmarks/anal1v.pdf"
# name = "Architecture Essay.pdf"
# name = "Halliday - Fundamentals of Physics Extended 9th-HQ.pdf"
# name = "Xenoblade The Secret Files English Translation_v1-4.pdf"

#Basic finding of the ToC page, maybe use nlp for better to filter out "brief contents" and other edge cases
def find_toc(name):
    with open(name, 'rb') as f:
        pdf_reader = PdfReader(f)
        for i in range(0, len(pdf_reader.pages)):
            current_page = pdf_reader.pages[i]
            text = current_page.extract_text()
            if text == None or text == "":
                print(f"Unable to extract text from page {i}")
                continue
            print(f"Page {i}: {text[:50]}")
            if "contents" in text.lower():
                return i
        print("Table of contents not found")
        return -1


def read_toc(name,starting_page = -2):
    if starting_page == -2:
        starting_page = find_toc(name)
    with open(name, "rb") as f:
        pdf_reader = PdfReader(f)
        current_page = starting_page
        outlines_added = 0
        writer = PdfWriter()
        is_first_page = True
        #loading writer
        for page in pdf_reader.pages:
            writer.add_page(page)
        current_parent_chapter = None
        writer.add_outline_item("Contents", starting_page)
        while current_page < len(pdf_reader.pages): #should never reach this termination condition
            loaded_counter = 0
            page_text = pdf_reader.pages[current_page].extract_text()
            if page_text == None: 
                current_page += 1
                print(f"Unable to extract text from page {current_page}")
                continue
            lines = page_text.split("\n")
            for line in lines:
                match = re.search(r'(\d+)\s*$', line)
                if match:
                    p = int(match.group(1))
                    title = line[:match.start()].strip()  # Remove common trailing characters
                    loaded_counter += 1
                    outlines_added += 1
                    
                    if is_first_page:
                        is_first_page = False
                        offset = find_offset(pdf_reader, starting_page, title, p)
                        print(f"Offset = {offset}")

                    #misc e.g. preface
                    if not re.search(r"[0-9]", title):
                        writer.add_outline_item(title, p+offset)
                        current_parent_chapter = None
                    #chapter 
                    if not re.search(r"[0-9].[0-9]", title):
                        current_parent_chapter = writer.add_outline_item(title, p+offset)
                    #subchapter
                    else:
                        writer.add_outline_item(title, p+offset, parent= current_parent_chapter)
                    print(f"Bookmarking: '{title}' on page {p + offset} (original page {p})")
                else:
                    continue
            current_page += 1
            if loaded_counter < 1: break
        
    #We avoid saying .pdf twice
    striped_name = name[:-4]
    with open(f"{striped_name}-Bookmarked.pdf", "wb") as f_out:
        writer.write(f_out)
    
    return outlines_added

def find_offset(pdf_reader, starting_page, chapter_name, listed_page, similarity_threshold = 70):
    current_page = starting_page + 1 #start search 1 page after chpt name is listed
    print(f"Chpt name: {chapter_name}")
    while current_page < len(pdf_reader.pages):
        page_text = pdf_reader.pages[current_page].extract_text()
        if not page_text:
            current_page += 1
            continue
        page_text = re.sub(r'\s+', ' ', page_text)
        page_text = page_text[:30+len(chapter_name)]#arbitrarily setting to 30 characters to account for any random stuff they might have
        similarity = fuzz.partial_ratio(page_text.lower(), chapter_name.strip().lower())
        print(f"Page {current_page}:\n{page_text}. Similarity = {similarity}")
        
        if similarity >= similarity_threshold:
            print(f"Match found on page {current_page} with similarity {similarity}")
            break
        current_page += 1

    
    return current_page - int(listed_page)




name = input("Please enter the path of the file: ").replace('"', '') #Removing quote marks as windows copy path adds these
# offset = int(input("Please enter the pdf page coresponding to book page 1, or -1 if unknown: "))
print(read_toc(name))



