import fpdf
import datetime

class PDF(fpdf.FPDF):

    def header(self):

        # insert logo
        self.image("util_images/logo.png", x=10, y=6, w=60, h=20)

        # position logo on the right
        #self.cell(80)

        self.set_font("Arial", size=16)

        date = datetime.date.today()
        self.cell(0, 10, str(date), align="R", ln=1)

        # set the font for the header, B=Bold
        self.set_font("Arial", style="B", size=24)

        # page title
        self.cell(0, 30, "Crystallography Report", border=0, ln=0, align="C")

        # insert a line break of 20 pixels
        self.ln(20)

    #----------------------------------------------------------------------------

    def footer(self):

        # position footer at 15mm from the bottom
        self.set_y(-15)

        # set the font, I=italic
        self.set_font("Arial", style="I", size=8)

        # display the page number and center it
        pageNum = "Page %s/{nb}" % self.page_no()
        self.cell(0, 10, pageNum, align="C")

    #-----------------------------------------------------------------------------

def create_pdf(list):

    name = list[0]
    well_image = list[1]
    project_name = list[2]
    target_name = list[3]
    plate_name = list[4]
    date = list[5]

    notes = list[6]

    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Arial", size=14)

    pdf.cell(0, 15, "Prepared by: " + name, align="C", ln=1)

    pdf.image(well_image, 30, 55, w=153, h=115)

    pdf.ln(130)

    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(50, 0, "Project name: ", align="R", ln=0)

    pdf.set_font("Arial", size=14)
    pdf.cell(0, 0, project_name, align="L", ln=1)

    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(50, 18, "Target name: ", align="R", ln=0)

    pdf.set_font("Arial", size=14)
    pdf.cell(0, 18, target_name, align="L", ln=1)

    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(50, 0, "Plate name: ", align="R", ln=0)

    pdf.set_font("Arial", size=14)
    pdf.cell(0, 0, plate_name, align="L", ln=1)

    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(50, 18, "Date of image: ", align="R", ln=0)

    pdf.set_font("Arial", size=14)
    pdf.cell(0, 18, date, align="L", ln=1)

    pdf.ln(10)

    pdf.set_font("Arial", size=14, style="B")
    pdf.cell(50, 0, "Notes: ", align="R", ln=0)

    pdf.set_font("Arial", size=14)
    pdf.cell(0, 0, notes, align="L", ln=1)

    pdf.output("tutorial.pdf")

