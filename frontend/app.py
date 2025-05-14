import time

import dotenv
import requests
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from streamlit.runtime.uploaded_file_manager import UploadedFile

dotenv.load_dotenv()

BACKEND_URL = dotenv.dotenv_values().get("BACKEND_URL", "http://backend:5000")

st.title("🔍 Ask your PDFs")


################################### Sidebar ###################################
def upload_files(uploaded_files: list[UploadedFile], upload_space: DeltaGenerator):
	files = [("files", (file.name, file, "application/pdf")) for file in uploaded_files]
	r = requests.post(f"{BACKEND_URL}/documents", files=files)

	if r.status_code == 200:
		data = r.json()
		upload_space.success(data.get("message", "Files uploaded successfully!"))
		upload_space.write(f"Documents indexed: {data.get('documents_indexed', 0)}")
		upload_space.write(f"Chunks created: {data.get('total_chunks', 0)}")
	else:
		upload_space.error("Failed to upload files.")


def handle_upload_button(uploaded_files: list[UploadedFile] | None, upload_space: DeltaGenerator):
	if not uploaded_files:
		upload_space.warning("Please upload at least one PDF file.")
		return
	# Check if the files are PDFs
	for file in uploaded_files:
		if file.type != "application/pdf":
			upload_space.error(f"{file.name} is not a PDF file.")
			break
	else:
		upload_warning = upload_space.empty()
		upload_warning.warning("Uploading files...")
		upload_files(uploaded_files, upload_space)
		# Wait for 2 seconds to show the upload message
		time.sleep(2)
		upload_warning.empty()


def handle_delete_data_button(delete_data_space: DeltaGenerator):
	r = requests.delete(f"{BACKEND_URL}/documents")
	if r.ok:
		delete_data_space.success("All data deleted successfully!")
	else:
		delete_data_space.error("Failed to delete data.")
	time.sleep(3)
	delete_data_space.empty()


def build_sidebar():
	# description
	st.sidebar.header("🤖 Ask your PDFs")
	st.sidebar.write(
		"Upload your PDF files and ask questions about their content.",
		"The server will handle the processing.",
	)
	st.sidebar.write(
		"**Note:** The document processing may take some time, depending on the size of the files.",
	)
	st.sidebar.header("🔧 Settings")
	# add a button to delete all data from the backend
	if st.sidebar.button("Delete all data", help="Delete all documents and chunks in the database."):
		st.sidebar.warning("Are you sure you want to delete all data? This action cannot be undone.")
		delete_data_space = st.sidebar.empty()
		st.sidebar.button("Confirm", on_click=handle_delete_data_button, args=(delete_data_space,))
	# PDF Upload in Sidebar
	st.sidebar.header("📄 Upload")

	uploaded_files = st.sidebar.file_uploader(
		"Upload your PDFs",
		type=["pdf"],
		accept_multiple_files=True,
		label_visibility="collapsed",
	)
	# add a button to upload the files
	upload_space = st.sidebar.empty()
	st.sidebar.button("Upload", on_click=handle_upload_button, args=(uploaded_files, upload_space))


build_sidebar()
# Main area: question input
st.subheader("Ask a question about your PDFs:")

question = st.text_input("Your question")

if st.button("Submit Question"):
	if not question:
		st.warning("Please enter a question.")
	else:
		payload = {"question": question}
		r = requests.post(f"{BACKEND_URL}/question", json=payload)
		if r.status_code == 200:
			response = r.json()
			answer = response.get("answer")
			chunks = response.get("chunks")
			st.write(f"**Answer:** {answer}")
			if chunks:
				st.write("**Relevant texts:**")
				# make the following list collapsible
				with st.expander("Show relevant texts", expanded=False, icon="📄"):
					# show the chunks in a list
					st.write("Relevant texts:")
					# show each chunk in a list
					for chunk in chunks:
						st.write(f"- {chunk}")
			else:
				st.error("Failed to get answer from backend.")
