from PyPDF2 import PdfReader, PdfWriter
import re
#TODO Use AI to determine page offset

name = "anal1v.pdf"
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
            if "contents" in text.lower():
                return i
        print("Table of contents not found")
        return -1


def read_toc(name, offset, starting_page = -2):
    if starting_page == -2:
        starting_page = find_toc(name)
    with open(name, "rb") as f:
        pdf_reader = PdfReader(f)
        current_page = starting_page
        outlines_added = 0
        writer = PdfWriter()
        offset = offset
        # is_first_page = True
        for page in pdf_reader.pages:
            writer.add_page(page)
        current_parent_chapter = None
        while current_page < len(pdf_reader.pages): #should never reach this termination condition
            loaded_counter = 0
            page_text = pdf_reader.pages[current_page].extract_text()
            if page_text == None: 
                current_page += 1
                print(f"Unable to extract text from page {current_page}")
                continue
            lines = page_text.split("\n")
            for line in lines:
                # print(line)
                delimiter = line.rfind(' ')
                p = line[delimiter:].strip()
                # print(f"p = {p}")
                if p.isdigit(): 
                    loaded_counter += 1
                    outlines_added += 1
                    title = line[:delimiter]
                    p = int(p)
                    # print(f"Title: {title}, pg: {p}")
                    
                    # if is_first_page:
                    #     is_first_page = False
                    #     offset = find_offset(pdf_reader, starting_page, title, p)
                    #     print(f"Offset = {offset}")

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
                    print(f"p = {p}, offset = {offset}, Added page = {p+offset}")
                else:
                    continue
            current_page += 1
            if loaded_counter < 1: break
    with open(f"{name}-Bookmarked.pdf", "wb") as f_out:
        writer.write(f_out)
    
    return outlines_added

# def find_offset(pdf_reader, starting_page, chapter_name, listed_page):
#     current_page = starting_page + 1 #start search 1 page after chpt name is listed
#     print(f"Chpt name: {chapter_name}")
#     while current_page < len(pdf_reader.pages):
#         page_text = pdf_reader.pages[current_page].extract_text()
#         page_text.strip()
#         page_text = re.sub(r' +', ' ', page_text)
#         page_text = page_text[:30+len(chapter_name)]#arbitrarily setting to 30 characters to account for any random stuff they might have
#         print(f"Page {current_page}:\n{page_text}")
#         if chapter_name.lower() in page_text.lower():
#             break
#         current_page += 1

    
#     return current_page - int(listed_page)




# print(find_toc(name))
offset = int(input("Please enter offset(2 less than book page 1): "))
print(read_toc(name, offset))
# with open(name, 'rb') as f:
#         pdf = PdfReader(f)
#         print(pdf.pages[29].extract_text())


