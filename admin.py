import time
import streamlit as st
from utils.printer import get_printer_list, get_printer_status, print_file, print_label
from utils.config import save_system_config
from utils.logger import logger


test_file = "utils/fixtures/test.txt"

def system_config_tab():
    # st.header("System")
    options = get_printer_list()
    
    # Create a dropdown menu using selectbox
    selected_option = st.selectbox('Choose a printer:', options)
    
    # Clear status cache when printer selection changes
    if 'last_selected_printer' not in st.session_state:
        st.session_state.last_selected_printer = None
    
    if selected_option != st.session_state.last_selected_printer:
        logger.info(f"Printer selection changed to: {selected_option}")
        st.session_state.last_selected_printer = selected_option
        st.session_state.printer_status = None  # Clear status cache
    
    # Display printer status
    if selected_option:
        # Get fresh status if cache is cleared
        if st.session_state.printer_status is None:
            st.session_state.printer_status = get_printer_status(selected_option)
            logger.info(f"Printer {selected_option} status: {st.session_state.printer_status}")
        
        status = st.session_state.printer_status
        status_color = {
            "Idle": "green",
            "Active": "blue",
            "Offline": "red",
            "Error": "red",
            "Unknown": "gray"
        }.get(status, "red")
        
        st.markdown(f"**Printer Status:** <span style='color: {status_color}'>{status.upper()}</span>", unsafe_allow_html=True)
        
        # Add test print section
        # st.subheader("Test Print")
        # test_text = st.text_area("Enter text to print:", height=100)
        
        ifdisable = (status !='Idle')
        if st.button("打印测试", type="secondary", disabled=ifdisable):
            logger.info(f"Starting test print on printer: {selected_option}")
            with st.spinner("Printing..."):
                success, error = print_label(test_file, selected_option)
                time.sleep(2)
                # if success
                if success:
                    logger.info(f"Test print completed successfully on printer: {selected_option}")
                    st.success("Test print completed successfully!")
                else:
                    logger.error(f"Test print failed on printer: {selected_option} wih error {error}")
                    st.error(f"Test print failed with error {error} . Please check the printer status.")
    
    st.markdown("---")
    # Add button to save selected printer
    if st.button("Using this Printer", type="primary"):
        try:
            # with open(config.SYSTEM_CONFIG_FILE, "w") as f:
            #     json.dump({"printer": selected_option}, f)
            save_system_config({"printer": selected_option})
            logger.info(f"Set {selected_option} as default printer")
            st.success(f"Successfully set {selected_option} as the default printer!")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            logger.error(f"Error saving printer configuration: {str(e)}")
            st.error(f"Error saving printer configuration: {str(e)}")


st.title("🛠️ Admin Panel")

system_config_tab()