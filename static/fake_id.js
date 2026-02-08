let selectedType = null;
let generatedFile = null;

function selectIDType(type) {
    selectedType = type;
    
    // Remove active class from all cards
    document.querySelectorAll('.id-card').forEach(card => {
        card.classList.remove('active');
    });
    
    // Hide all forms
    document.querySelectorAll('.form-container').forEach(form => {
        form.classList.remove('active');
    });
    
    // Hide preview
    document.getElementById('preview').classList.remove('active');
    
    // Show selected form
    const selectedCard = event.target.closest('.id-card');
    selectedCard.classList.add('active');
    document.getElementById(`${type}-form`).classList.add('active');
    
    // Scroll to form
    setTimeout(() => {
        document.getElementById(`${type}-form`).scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

async function generateID(type) {
    let data = { type: type };
    
    // Validate and collect data based on type
    if (type === 'aadhar') {
        const name = document.getElementById('aadhar-name').value.trim();
        const dob = document.getElementById('aadhar-dob').value;
        const gender = document.getElementById('aadhar-gender').value;
        const address = document.getElementById('aadhar-address').value.trim();
        
        if (!name || !dob || !address) {
            alert('Please fill all required fields!');
            return;
        }
        
        data = { type, name, dob, gender, address };
    }
    else if (type === 'pan') {
        const name = document.getElementById('pan-name').value.trim();
        const father_name = document.getElementById('pan-father').value.trim();
        const dob = document.getElementById('pan-dob').value;
        const pan_number = document.getElementById('pan-number').value.trim();
        
        if (!name || !father_name || !dob) {
            alert('Please fill all required fields!');
            return;
        }
        
        data = { type, name, father_name, dob, pan_number };
    }
    else if (type === 'certificate') {
        const name = document.getElementById('cert-name').value.trim();
        const course = document.getElementById('cert-course').value.trim();
        const cert_type = document.getElementById('cert-type').value;
        const date = document.getElementById('cert-date').value;
        
        if (!name || !course || !date) {
            alert('Please fill all required fields!');
            return;
        }
        
        data = { type, name, course, cert_type, date };
    }
    
    // Show loading
    document.getElementById('loading').style.display = 'block';
    
    try {
        const response = await fetch('/generate-fake-id', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            generatedFile = result.file;
            
            // Show preview
            document.getElementById('preview-img').src = `/generated/${result.file}`;
            document.getElementById('preview').classList.add('active');
            
            // Scroll to preview
            setTimeout(() => {
                document.getElementById('preview').scrollIntoView({ behavior: 'smooth' });
            }, 100);
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Failed to generate ID: ' + error.message);
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

function downloadGenerated() {
    if (generatedFile) {
        window.location.href = `/generated/${generatedFile}`;
    }
}

function resetForm() {
    // Hide preview
    document.getElementById('preview').classList.remove('active');
    
    // Clear all forms
    document.querySelectorAll('input[type="text"], input[type="date"], textarea').forEach(input => {
        input.value = '';
    });
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Set today's date as default for date inputs
document.addEventListener('DOMContentLoaded', function() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('cert-date').value = today;
});
