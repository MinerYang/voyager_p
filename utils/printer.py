import logging
import streamlit as st
import cups
import time
from utils.config import system_config

print_options = {
    "media": "w100h70",
    "fit-to-page": "True",
    "number-up": "1",
    "page-left": "0",
    "page-right": "0",
    "page-top": "0",
    "page-bottom": "0",
    "cpi": "16",
    "lpi": "8",
}

def get_printer_list():
    """Get a list of available printers."""
    try:
        conn = cups.Connection()
        printers = conn.getPrinters()
        return list(printers.keys())
    except Exception as e:
        logging.error(f"Error getting printer list: {str(e)}")
        return []

def get_printer_status(printer_name):
    conn = cups.Connection()
    printers = conn.getPrinters()
    printer_info = printers[printer_name]
    logging.info(f"raw printer_info is: {printer_info}")

    # Get printer-state
    state = printer_info.get('printer-state')
    # Map the state to a human-readable string
    status_map = {
        3: "idle",
        4: "active",
        5: "offline",
        6: "error"
    }.get(state, "Unknown")

    # Get printer-state-reasons
    """
    none: No issues; the printer is functioning normally.

    media-needed: The printer requires more paper.

    toner-low: The printer's toner is low.

    toner-empty: The printer is out of toner.

    marker-supply-low: Low ink levels.

    marker-supply-empty: Out of ink.
    """
    reasons = printer_info.get('printer-state-reasons', [])
    if isinstance(reasons, str):
        reasons = [reasons] 
    # add a check to see if the printer is idle and has reasons
    if state == 3:  # Idle
        if reasons and reasons[0] != 'none':
            # Idle but has some reasons (e.g., media-needed, toner-low)
            return reasons[0]
        else:
            return "Idle"
    elif state == 4:
        return "Active"
    elif state == 5:
        return "Offline"
    elif state == 6:
        return " Error"
    else:
        return f"Unknown (state={state})" # Ensure it's a list
    
    # reasons_message = ", ".join(reasons) if reasons else "No additional information"
    # return status_map.get(printer_state, 'Unknown')

def print_label(filename, printer_name):
    targetfile = save_label_text(filename)
    try:
        conn = cups.Connection()
        if printer_name is None:
            printer_name = system_config.get_printer()
        if not printer_name:
            # logging.error("No printer selected")
            return False, Exception("No printer selected")
        logging.info(f"Will use printer {printer_name} to print {targetfile}")
        job_id = conn.printFile(printer_name, targetfile, f"Job for {targetfile}", print_options)
        logging.info("Print job submitted successfully!")
        # Wait for job to complete with timeout
        timeout = 15  # 15 seconds timeout
        start_time = time.time()
        while True:
            # Check for timeout, cancel job after timeout
            if time.time() - start_time > timeout:
                try:
                    # Cancel the print job
                    conn.cancelJob(job_id)
                    logging.error("Print job timed out after {timeout} seconds and was cancelled")
                except cups.IPPError as e:
                    # logging.error(f"Print job timed out and failed to cancel: {str(e)}")
                    return False, e
                return False, Exception("Timeout and cancel job")
            
            try:
                job_info = conn.getJobAttributes(job_id)
                job_state = job_info.get('job-state')
                
                if job_state == 9:  # Completed
                    logging.info(f"Print job completed successfully!")
                    return True, None
                elif job_state in [7, 8]:  # Error or Cancelled
                    logging.error(f"Print job failed with state: {job_state}")
                    return False, e
                    
                time.sleep(1)  # Check status every second    
            except cups.IPPError as e:
                logging.error(f"Error checking job status: {str(e)}")
                return False, e
    except cups.IPPError as e:
        logging.error(f"Printer error: {str(e)}")
        return False, e
    except FileNotFoundError as e:
        logging.error(f"File error: {str(e)}")
        return False,e
    except Exception as e:
        logging.error(f"Unexpected error during printing: {str(e)}")
        return False, e
    except Exception as e:
        logging.error(f"Unexpected error during printing: {str(e)}")
        return False, e


def print_file(filename, printer_name=None):
    targetfile = save_label_text(filename)
    try:
        # Create status container for progress updates
        status_container = st.empty()
        status_container.info("Starting print job...")
        
        # Step 2: Connect to printer
        status_container.info("Connecting to printer...")
        conn = cups.Connection()
        
        # Step 3: Submit print job
        if printer_name is None:
            printer_name = system_config.get_printer()
        if not printer_name:
            status_container.error("No printer selected")
            return False
        logging.info(f"Will use printer {printer_name} to print {targetfile}")
        status_container.info("Submitting print job...")
        job_id = conn.printFile(printer_name, targetfile, f"Job for {targetfile}", print_options)
        
        # Step 4: Monitor job status
        status_container.info("Print job submitted successfully!")
        
        # Wait for job to complete with timeout
        timeout = 15  # 60 seconds timeout
        start_time = time.time()
        
        while True:
            # Check for timeout
            if time.time() - start_time > timeout:
                try:
                    # Cancel the print job
                    conn.cancelJob(job_id)
                    status_container.error("Print job timed out after 60 seconds and was cancelled")
                    status_container.error("Please ask admin to check the printer status and try again")
                    logging.error(f"Print job timed out after 60 seconds and was cancelled")
                    logging.error(f"Print job timed out after 60 seconds and was cancelled")
                except cups.IPPError as e:
                    status_container.error(f"Print job timed out and failed to cancel: {str(e)}")
                    logging.error(f"Print job timed out and failed to cancel: {str(e)}")
                    logging.error(f"Print job timed out and failed to cancel: {str(e)}")
                return False
                
            try:
                job_info = conn.getJobAttributes(job_id)
                job_state = job_info.get('job-state')
                
                if job_state == 9:  # Completed
                    status_container.success("Print job completed successfully!")
                    logging.info(f"Print job completed successfully!")
                    return True
                elif job_state in [7, 8]:  # Error or Cancelled
                    status_container.error(f"Print job failed with state: {job_state}")
                    logging.error(f"Print job failed with state: {job_state}")
                    return False
                    
                time.sleep(1)  # Check status every second
                
            except cups.IPPError as e:
                status_container.error(f"Error checking job status: {str(e)}")
                logging.error(f"Error checking job status: {str(e)}")
                return False
            
    except cups.IPPError as e:
        st.error(f"Printer error: {str(e)}")
        return False
    except FileNotFoundError as e:
        st.error(f"File error: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Unexpected error during printing: {str(e)}")
        return False 
    except Exception as e:
        st.error(f"Unexpected error during printing: {str(e)}")
        return False


def wrap_chinese(text, width):
    lines = []
    for paragraph in text.splitlines():
        line = ''
        for char in paragraph:
            line += char
            if len(line) >= width:
                lines.append(line)
                line = ''
        if line:
            lines.append(line)
    return lines


def save_label_text(originfile, max_chars=25, max_lines=20):
    with open(originfile, 'r') as file:
        content = file.read()
    wrapped_lines = []
    wrapped_lines = wrap_chinese(content, max_chars)
    # Wrap each paragraph without splitting words
    # for paragraph in text.split('\n'):
    #     lines = textwrap.wrap(paragraph, width=max_chars, break_long_words=False, replace_whitespace=False)
    #     print(lines)
    #     wrapped_lines.extend(lines)

    # Split into label-sized chunks
    labels = [wrapped_lines[i:i + max_lines] for i in range(0, len(wrapped_lines), max_lines)]
    targetfile = originfile.replace(".txt", "-label.txt")
    with open(targetfile, "w", encoding="utf-8") as f:
        for label in labels:
            # Left-align and pad each line to max_chars for uniform width
            # aligned = [line.ljust(max_chars) for line in label]
            aligned = [("          " + line).ljust(max_chars + 5) for line in label]
            f.write('\n'.join(aligned))
            f.write('\n\n' + '-' * max_chars + '\n\n')  # Label separator

    return targetfile
