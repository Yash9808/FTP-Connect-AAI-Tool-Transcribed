import os
import ftplib
import assemblyai as aai
import streamlit as st

def transcribe_audio(file_path, api_key):
    aai.settings.api_key = api_key
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(file_path)
    return transcript.text

def connect_ftp(ftp_host, ftp_user, ftp_pass):
    try:
        ftp = ftplib.FTP(ftp_host)
        ftp.login(ftp_user, ftp_pass)
        folders = ftp.nlst()
        ftp.quit()
        return folders, None
    except Exception as e:
        return None, str(e)

def fetch_from_ftp(ftp_host, ftp_user, ftp_pass, ftp_folder, api_key):
    ftp = ftplib.FTP(ftp_host)
    ftp.login(ftp_user, ftp_pass)
    ftp.cwd(ftp_folder)
    filenames = ftp.nlst()
    results = {}
    
    os.makedirs("./downloads", exist_ok=True)
    
    for filename in filenames:
        local_path = f"./downloads/{filename}"
        with open(local_path, 'wb') as f:
            ftp.retrbinary(f'RETR {filename}', f.write)
        results[filename] = transcribe_audio(local_path, api_key)
    
    ftp.quit()
    return results

st.title("FTP Audio Transcriber with AssemblyAI")

api_key = st.text_input("Enter your AssemblyAI API Key", type="password")

st.subheader("Upload Audio Files for Transcription")
uploaded_files = st.file_uploader("Upload audio files", accept_multiple_files=True)
if st.button("Transcribe Uploaded Files"):
    if not api_key:
        st.error("Please enter your AssemblyAI API Key")
    elif not uploaded_files:
        st.error("Please upload at least one audio file")
    else:
        results = {}
        os.makedirs("./uploads", exist_ok=True)
        for file in uploaded_files:
            file_path = os.path.join("./uploads", file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            results[file.name] = transcribe_audio(file_path, api_key)
        
        for filename, transcript in results.items():
            st.subheader(f"Transcription for {filename}")
            st.text_area("Transcript", transcript, height=200)

st.subheader("Connect to FTP to Fetch Audio Files")
ftp_host = st.text_input("FTP Host")
ftp_user = st.text_input("FTP Username")
ftp_pass = st.text_input("FTP Password", type="password")

if st.button("Connect & List Folders"):
    folders, error = connect_ftp(ftp_host, ftp_user, ftp_pass)
    if error:
        st.error(f"Failed to connect: {error}")
    else:
        folder = st.selectbox("Select an FTP folder", folders)
        if st.button("Fetch & Transcribe Audio Files"):
            if not api_key:
                st.error("Please enter your AssemblyAI API Key")
            else:
                with st.spinner("Fetching and transcribing files..."):
                    results = fetch_from_ftp(ftp_host, ftp_user, ftp_pass, folder)
                    for filename, transcript in results.items():
                        st.subheader(f"Transcription for {filename}")
                        st.text_area("", transcript, height=200)

if __name__ == "__main__":
    st.title("FTP Audio Transcriber App")
