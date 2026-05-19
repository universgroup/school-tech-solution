        
        let currentTab = 'infos_personnel';
        
        function switchTab(tabId) {
            // Hide all tab panes
            const panes = document.querySelectorAll('.tab-pane');
            panes.forEach(pane => {
                pane.classList.remove('active');
            });
            
            // Show selected tab pane
            const selectedPane = document.getElementById(tabId);
            selectedPane.classList.add('active');
            
            // Update active tab button
            const buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Find and activate the clicked button
            const clickedBtn = Array.from(buttons).find(btn => 
                btn.textContent.toLowerCase().includes(tabId === 'infos_personnel' ? 'infos_personnel' : 
                                                       tabId === 'adresse_personnelle' ? 'adresse_personnelle' : 'inscription')
            );
            if (clickedBtn) {
                clickedBtn.classList.add('active');
            }
            
            // Update current tab
            currentTab = tabId;
            
            // Update progress indicator
            updateProgressIndicator(tabId);
        }
        
        function nextTab() {
            if (currentTab === 'infos_personnel') {
                if (validatePersonalTab()) {
                    switchTab('adresse_personnelle');
                }
            } else if (currentTab === 'adresse_personnelle') {
                if (validateAddressTab()) {
                    switchTab('inscription');
                }
            }
        }
        
        function previousTab() {
            if (currentTab === 'adresse_personnelle') {
                switchTab('infos_personnel');
            } else if (currentTab === 'inscription') {
                switchTab('adresse_personnelle');
            }
        }
        
        function validatePersonalTab() {
            const firstName = document.getElementById('firstName').value;
            const lastName = document.getElementById('lastName').value;
            const email = document.getElementById('email').value;
            
            if (!firstName || !lastName || !email) {
                alert('Please fill in all required fields (First Name, Last Name, Email)');
                return false;
            }
            
            if (!isValidEmail(email)) {
                alert('Please enter a valid email address');
                return false;
            }
            
            // Mark tab as completed
            markTabCompleted('personal');
            return true;
        }
        
        function validateAddressTab() {
            const street = document.getElementById('street').value;
            const city = document.getElementById('city').value;
            const state = document.getElementById('state').value;
            const zip = document.getElementById('zip').value;
            const country = document.getElementById('country').value;
            
            if (!street || !city || !state || !zip || !country) {
                alert('Please fill in all required address fields');
                return false;
            }
            
            // Mark tab as completed
            markTabCompleted('address');
            return true;
        }
        
        function isValidEmail(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        }
        
        function markTabCompleted(tabId) {
            let stepNumber = 1;
            if (tabId === 'personal') stepNumber = 1;
            else if (tabId === 'address') stepNumber = 2;
            else if (tabId === 'preferences') stepNumber = 3;
            
            const stepElement = document.getElementById(`step${stepNumber}`);
            if (stepElement && !stepElement.classList.contains('completed')) {
                stepElement.classList.add('completed');
            }
        }
        
        function updateProgressIndicator(tabId) {
            // Reset all steps
            for (let i = 1; i <= 3; i++) {
                const step = document.getElementById(`step${i}`);
                step.classList.remove('active');
            }
            
            // Set active step
            let activeStep = 1;
            if (tabId === 'personal') activeStep = 1;
            else if (tabId === 'address') activeStep = 2;
            else if (tabId === 'preferences') activeStep = 3;
            
            const activeStepElement = document.getElementById(`step${activeStep}`);
            activeStepElement.classList.add('active');
        }
        
        function resetForm() {
            // Reset all input fields
            const inputs = document.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                if (input.type === 'text' || input.type === 'email' || input.type === 'tel' || 
                    input.type === 'date' || input.type === 'number' || input.tagName === 'TEXTAREA') {
                    input.value = '';
                } else if (input.type === 'radio' || input.type === 'checkbox') {
                    input.checked = false;
                } else if (input.tagName === 'SELECT') {
                    input.selectedIndex = 0;
                }
            });
            
            // Reset progress indicator
            for (let i = 1; i <= 3; i++) {
                const step = document.getElementById(`step${i}`);
                step.classList.remove('completed');
                if (i === 1) {
                    step.classList.add('active');
                } else {
                    step.classList.remove('active');
                }
            }
            
            // Go back to first tab
            switchTab('personal');
            
            // Show success message
            alert('Form has been reset');
        }
        
        function submitForm() {
            // Validate all required fields
            if (!validatePersonalTab() || !validateAddressTab()) {
                alert('Please complete all required fields in Personal Info and Address tabs');
                return;
            }
            
            // Collect form data
            const formData = {
                firstName: document.getElementById('firstName').value,
                lastName: document.getElementById('lastName').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                gender: document.getElementById('gender').value,
                street: document.getElementById('street').value,
                city: document.getElementById('city').value,
                state: document.getElementById('state').value,
                zip: document.getElementById('zip').value,
                country: document.getElementById('country').value,
                occupation: document.getElementById('occupation').value,
                bio: document.getElementById('bio').value,
                interests: Array.from(document.querySelectorAll('input[name="interests"]:checked')).map(cb => cb.value),
                newsletter: document.querySelector('input[name="newsletter"]:checked')?.value,
                contact: document.querySelector('input[name="contact"]:checked')?.value
            };
            
            console.log('Form Data:', formData);
            alert('Form submitted successfully!\nCheck console for data.');
            
            // Here you can add AJAX call to send data to server
        }