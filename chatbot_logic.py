def get_response(user_input):
    user_input = user_input.lower()

    if "admission" in user_input:
        return "Admissions information is available on the NIT Jalandhar official website under the Admissions section."

    elif "placement" in user_input:
        return "NIT Jalandhar has an active placement cell. Placement statistics and recruiters are listed on the Placements page."

    elif "hostel" in user_input:
        return "NIT Jalandhar provides separate hostel facilities for boys and girls with mess and Wi-Fi."

    elif "fee" in user_input or "fees" in user_input:
        return "Fee structure details can be found on the official website under Academics or Admissions."

    elif "department" in user_input:
        return "NIT Jalandhar has multiple departments including CSE, ECE, ME, CE, EE, and more."

    elif "faculty" in user_input:
        return "Faculty details are available department-wise on the NIT Jalandhar website."

    elif "library" in user_input:
        return "The institute has a central library with digital and physical resources for students."

    elif "contact" in user_input:
        return "You can contact NIT Jalandhar through the contact details provided on the official website."

    elif "location" in user_input or "address" in user_input:
        return "NIT Jalandhar is located in Jalandhar, Punjab, India."

    elif "hello" in user_input or "hi" in user_input:
        return "Hello! I am the NITJ Chatbot. How can I assist you today?"

    else:
        return "Sorry, I could not understand your query. Please visit the official NIT Jalandhar website for more details."
