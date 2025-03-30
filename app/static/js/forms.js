document.addEventListener('DOMContentLoaded', function() {
    // Initialize Select2 for multiple select fields with improved configuration
    if (typeof Select2 !== 'undefined') {
        $('.select2-multiple').select2({
            theme: 'default',
            placeholder: 'Select your interests...',
            allowClear: true,
            closeOnSelect: false,
            width: '100%',
            maximumSelectionLength: 10,
            minimumInputLength: 0,
            dropdownParent: $('.form-container'),
            templateResult: formatInterestOption,
            templateSelection: formatInterestSelection,
            language: {
                noResults: function() {
                    return "No matching interests found";
                },
                maximumSelected: function() {
                    return "You can select up to 10 interests";
                }
            }
        });

        // Add custom styling to Select2 dropdown
        $('.select2-multiple').on('select2:open', function() {
            setTimeout(function() {
                $('.select2-dropdown').addClass('animate-fade-in');
                $('.select2-search__field').focus();
            }, 0);
        });

        // Handle selection changes
        $('.select2-multiple').on('select2:select select2:unselect', function(e) {
            const selectedCount = $(this).val() ? $(this).val().length : 0;
            updateInterestCounter(selectedCount);
        });
    }

    // Format interest options in dropdown
    function formatInterestOption(interest) {
        if (!interest.id) return interest.text;
        
        const interestIcons = {
            'software_development': '💻',
            'data_science': '📊',
            'ai_ml': '🤖',
            'cybersecurity': '🔒',
            'cloud_computing': '☁️',
            'devops': '⚙️',
            'web_development': '🌐',
            'mobile_development': '📱',
            'ui_ux': '🎨',
            'product_management': '📋',
            'digital_marketing': '📢',
            'business_analytics': '📈',
            'project_management': '📅',
            'blockchain': '⛓️',
            'iot': '🔌',
            'ar_vr': '👓',
            'game_development': '🎮',
            'technical_writing': '✍️',
            'qa_testing': '🔍',
            'database_admin': '🗄️'
        };

        const icon = interestIcons[interest.id] || '🎯';
        return $(`<span><span class="interest-icon">${icon}</span> ${interest.text}</span>`);
    }

    // Format selected interests
    function formatInterestSelection(interest) {
        if (!interest.id) return interest.text;
        const interestIcons = {
            'software_development': '💻',
            'data_science': '📊',
            'ai_ml': '🤖',
            'cybersecurity': '🔒',
            'cloud_computing': '☁️',
            'devops': '⚙️',
            'web_development': '🌐',
            'mobile_development': '📱',
            'ui_ux': '🎨',
            'product_management': '📋',
            'digital_marketing': '📢',
            'business_analytics': '📈',
            'project_management': '📅',
            'blockchain': '⛓️',
            'iot': '🔌',
            'ar_vr': '👓',
            'game_development': '🎮',
            'technical_writing': '✍️',
            'qa_testing': '🔍',
            'database_admin': '🗄️'
        };
        const icon = interestIcons[interest.id] || '🎯';
        return $(`<span class="selected-interest"><span class="interest-icon">${icon}</span> ${interest.text}</span>`);
    }

    // Update interest counter
    function updateInterestCounter(count) {
        const counterEl = document.querySelector('.interest-counter');
        if (!counterEl) {
            const container = document.querySelector('.select2-container').parentElement;
            const counter = document.createElement('small');
            counter.className = 'interest-counter text-muted mt-2 d-block';
            container.appendChild(counter);
        }
        const counterText = count === 1 ? '1 interest selected' : `${count} interests selected`;
        document.querySelector('.interest-counter').textContent = counterText;
    }

    // Add custom styles for Select2
    const style = document.createElement('style');
    style.textContent = `
        .select2-container--default .select2-selection--multiple {
            background-color: var(--background) !important;
            border: 2px solid var(--border) !important;
            border-radius: 8px !important;
            min-height: 120px !important;
            padding: 8px !important;
        }

        .select2-container--default .select2-selection--multiple .select2-selection__choice {
            background-color: var(--primary) !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 6px 10px !important;
            margin: 4px !important;
            color: white !important;
            font-size: 0.9rem !important;
            display: flex !important;
            align-items: center !important;
        }

        .interest-icon {
            margin-right: 8px;
            font-size: 1.1em;
        }

        .select2-container--default .select2-results__option {
            padding: 8px 12px !important;
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
        }

        .select2-container--default .select2-results__option--highlighted[aria-selected] {
            background-color: var(--primary) !important;
        }

        .select2-dropdown {
            animation: fadeIn 0.2s ease-out;
            border: 2px solid var(--border) !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }

        .select2-search__field {
            border-radius: 4px !important;
            padding: 6px 8px !important;
        }

        .select2-container--default .select2-selection--multiple .select2-selection__choice__remove {
            color: white !important;
            margin-right: 8px !important;
            border: none !important;
            background: none !important;
            opacity: 0.8 !important;
        }

        .select2-container--default .select2-selection--multiple .select2-selection__choice__remove:hover {
            opacity: 1 !important;
            background: none !important;
            color: white !important;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    `;
    document.head.appendChild(style);

    // Add sketch effect to form elements
    const formElements = document.querySelectorAll('.form-control, .btn, .alert');
    formElements.forEach(element => {
        element.classList.add('sketch-border');
    });

    // Animate form elements on page load
    const formContainer = document.querySelector('.form-container');
    if (formContainer) {
        formContainer.classList.add('animate-fade-in');
    }

    // Add floating label effect
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(control => {
        const wrapper = document.createElement('div');
        wrapper.classList.add('floating-label-wrapper');
        control.parentNode.insertBefore(wrapper, control);
        wrapper.appendChild(control);

        if (control.value !== '') {
            control.classList.add('has-value');
        }

        control.addEventListener('focus', () => {
            wrapper.classList.add('focused');
        });

        control.addEventListener('blur', () => {
            wrapper.classList.remove('focused');
            if (control.value !== '') {
                control.classList.add('has-value');
            } else {
                control.classList.remove('has-value');
            }
        });
    });

    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            button.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Form validation with custom styling
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();

                // Add shake animation to invalid fields
                const invalidFields = form.querySelectorAll(':invalid');
                invalidFields.forEach(field => {
                    field.classList.add('shake');
                    setTimeout(() => {
                        field.classList.remove('shake');
                    }, 600);
                });
            }

            form.classList.add('was-validated');
        });
    });

    // Password strength indicator
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        const meter = document.createElement('div');
        meter.classList.add('password-strength-meter');
        input.parentNode.appendChild(meter);

        input.addEventListener('input', () => {
            const strength = calculatePasswordStrength(input.value);
            updatePasswordStrengthMeter(meter, strength);
        });
    });
});

// Password strength calculator
function calculatePasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]/)) strength++;
    if (password.match(/[A-Z]/)) strength++;
    if (password.match(/[0-9]/)) strength++;
    if (password.match(/[^a-zA-Z0-9]/)) strength++;
    return strength;
}

// Update password strength meter
function updatePasswordStrengthMeter(meter, strength) {
    meter.className = 'password-strength-meter';
    switch(strength) {
        case 0:
        case 1:
            meter.classList.add('weak');
            break;
        case 2:
        case 3:
            meter.classList.add('medium');
            break;
        case 4:
        case 5:
            meter.classList.add('strong');
            break;
    }
}

// Add custom styles for password strength meter
const style = document.createElement('style');
style.textContent = `
    .password-strength-meter {
        height: 4px;
        background-color: var(--border);
        margin-top: 8px;
        border-radius: 2px;
        transition: all 0.3s ease;
    }

    .password-strength-meter.weak {
        background-color: var(--danger);
        width: 33%;
    }

    .password-strength-meter.medium {
        background-color: #f1c40f;
        width: 66%;
    }

    .password-strength-meter.strong {
        background-color: var(--success);
        width: 100%;
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }

    .shake {
        animation: shake 0.3s ease-in-out;
    }

    .floating-label-wrapper {
        position: relative;
        margin-bottom: 1rem;
    }

    .floating-label-wrapper label {
        position: absolute;
        top: 0;
        left: 12px;
        transform: translateY(-50%);
        background-color: var(--surface);
        padding: 0 8px;
        font-size: 0.875rem;
        color: var(--text-muted);
        transition: all 0.3s ease;
    }

    .floating-label-wrapper.focused label {
        color: var(--primary);
    }

    .ripple {
        position: absolute;
        border-radius: 50%;
        background-color: rgba(255, 255, 255, 0.3);
        width: 100px;
        height: 100px;
        margin-top: -50px;
        margin-left: -50px;
        animation: ripple 0.6s linear;
        pointer-events: none;
    }

    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style); 