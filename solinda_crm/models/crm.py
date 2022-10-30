import string
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
from dateutil import relativedelta

class BusinessType(models.Model):
    _name = 'business.type'
    _description = 'Business Type'
    
    name = fields.Char('Business Name')

class ProjectStatus(models.Model):
    _name = 'project.status'
    _description = 'Project Status'

    name = fields.Char('name')

class ProjectScheme(models.Model):
    _name = 'project.scheme'
    _description = 'Project Scheme'

    name = fields.Char('name')

class WastewaterType(models.Model):
    _name = 'wastewater.type'
    _description = 'Type Wastewater for Tertiary Treatment'
    
    name = fields.Char('name')

class TransportSurvey(models.Model):
    _name = 'transport.survey'
    _description = 'Transport Survey'
    
    name = fields.Char('name')

class PlantType(models.Model):
    _name = 'plant.type'
    _description = 'Plant Type'
    

    name = fields.Char('Name')

class NewInstallation(models.Model):
    _name = 'new.installation'
    _description = 'New Installation'

    name = fields.Char("Name")

class Refubrishment(models.Model):
    _name = 'refubrishment'
    _description = 'Refubrishment'

    name = fields.Char("Name")

class IndustrialDetail(models.Model):
    _name = 'industrial.detail'
    _description = 'Industrial Detail'

    name = fields.Char(string="Name")

class PreScreening(models.Model):
    _name = 'pre.screening'
    _description = "Pre-Screening"

    name = fields.Char("Name", required=True)
    pre_type = fields.Char("Type", required=True)
    opening = fields.Float("Opening (mm)", required=True)
    no_bypass = fields.Boolean("NO BYPASS")
    no_overflow = fields.Boolean("NO OVERFLOW")
    crm_id = fields.Many2one('crm.lead', "CRM")

class CoagulantType(models.Model):
    _name = 'coagulant.type'
    _description = "Type of Coagulant"

    name = fields.Char("Name")

class AdvancedTreatment(models.Model):
    _name = 'advanced.treatments'
    _description = 'Advanced Treatments'

    name = fields.Char("Name")

class OperationConditions(models.Model):
    _name = 'operation.conditions'
    _description = "Operation & Maintenance Conditions"

    name = fields.Char(string="Name")

class RawWaterCharacterizations(models.Model):
    _name = 'water.characterizations'
    _description = "Raw Water Characterizations"

    parameter = fields.Char(string="Parameter")
    unit = fields.Char(string="Unit")
    value = fields.Float(string="Value")
    remarks = fields.Char(string="Remarks")
    crm_id = fields.Many2one("crm.lead", string="CRM")

class TreatedWaterQuality(models.Model):
    _name = 'treated.quality'
    _description = 'Treated Water/Wastewater Quality'

    name = fields.Char("Name")
    effluent_standards = fields.Float("Effluent standards")
    target_value = fields.Float("Target Value")
    crm_id = fields.Many2one('crm.lead', string="CRM")
    uom = fields.Char(string="UoM")

class ExistingChemical(models.Model):
    _name = 'existing.chemical'
    _description = 'Existing Chemical Usage On Location (If any)'

    parameters = fields.Char('Parameters')
    average_daily = fields.Float('Average')
    min_daily = fields.Float('MIN')
    max_daily = fields.Float('MAX')
    remarks = fields.Char('Remarks')
    crm_id = fields.Many2one('crm.lead', string="CRM")

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # date_deadline = fields.Date('Expected Closing', required=True)
    tag_ids = fields.Many2many('crm.tag', string='Tags', required=True)

    # Type of business
    business_type_id = fields.Many2one('business.type', string='Business Type')

    # Plant Overview
    project_name = fields.Char('Project Name')
    country_id = fields.Many2one('res.country', string='Location (Country)')
    plant_type_id = fields.Many2one('plant.type', string='Plant Type')
    plant_start_date = fields.Date('Plant Start Date')

    # Reason for installing water/wastewater system
    new_installation = fields.Boolean(string='New Installation')
    req_new_ids = fields.Many2many('new.installation', string='Requirements')
    refubrishment = fields.Boolean(string="Refurbishment of an existing water/wastewater treatment plant")
    req_refubrish_ids = fields.Many2many('refubrishment', string="Requirements")
    is_further_process = fields.Boolean(string="Is the process followed by any further process?")
    treatment_process = fields.Char(string="If yes, what kind of treatment process is planned?")

    # Water Source Conditions
    ground_water = fields.Boolean('Ground Water')
    surface_water = fields.Selection([
        ('river', 'River'),
        ('lake', 'Lake or reservoir'),
    ], string='Surface Water')
    seawater = fields.Selection([
        ('intake', 'Open intake'),
        ('beach', 'Beach well'),
    ], string='Seawater')
    waste_water_treatment = fields.Selection([
        ('municipal', 'Municipal'),
        ('domestic', 'Domestic'),
        ('industrial', 'Industrial'),
    ], string='Wastewater for Tertiary Treatment')
    industrial_detail_id = fields.Many2one('industrial.detail', string="Industrial Detail")
    distance_from_rawwater = fields.Char('Distance from Raw Water Source to Treatment Plant')
    elevation_from_rawwater = fields.Char('Elevation from Raw Water Source to Treatment Plant')

    # Requested design capacity and pre-treatment
    average_capacity = fields.Float("Average design capacity (m3/d)")
    full_capacity = fields.Float("Full design capacity (m3/d)")
    peak_conditions = fields.Float("Peak Flow Conditions for a duration (m3/hr)")
    frequency = fields.Float("at a frequency (hr)")
    day_week = fields.Float("x per day/week")
    required_capacity_hr = fields.Float("Required capacity with one train out of service (m3/hr)")
    required_capacity_d = fields.Float("Required capacity with one train out of service (m3/d)")
    min_temperature = fields.Float("Minimum water temperature (C)")
    max_temperature = fields.Float("Maximum water temperature (C)")
    required_recovery = fields.Float("Required Recovery (%)")
    prescreening_ids = fields.One2many("pre.screening", "crm_id", string="Pre-Screening")
    is_coagulant = fields.Boolean("Is coagulant dosed?")
    coagulant_type_id = fields.Many2one('coagulant.type', string="Type of coagulant")
    advanced_treatments = fields.Many2many('advanced.treatments', string="Other advanced treatment(s)")
    operation_conditions = fields.Many2many('operation.conditions', string="Operation & Maintenance conditions at this plant")

    # Post-treatment process(es)
    ro = fields.Boolean("RO")
    chlorination = fields.Boolean("Chlorination")
    post_treatment_other = fields.Char("Other")

    # Maintenance
    sodium = fields.Boolean("Can sodium hypochlorite solution (3000 mg/L as Cl2) be used for the chemical cleaning of the membrane elements?")
    oxalic = fields.Boolean("Can oxalic acid solution (0.3-3.0%) be used for the chemical cleaning of the membrane elements?")
    plant_operation = fields.Boolean("Is there an automatic data collection & storage system for plant operation?")
    plant_reduced_capacity = fields.Boolean("Can the plant be stopped or operate at reduced capacity for maintenance?")

    # Raw water/wastewater Characterizations
    water_characterizations_ids = fields.One2many("water.characterizations", "crm_id", "Raw water/wastewater characterizations")

    #Treated Water/Wastewater Quality
    treated_quality_ids = fields.One2many('treated.quality', 'crm_id', string="Treated Water/Wastewater Quality")

    # Existing Chemical Usage On Location
    existing_chemical_ids = fields.One2many('existing.chemical', 'crm_id', string='Existing Chemical Usage On Location')
    
    #What are the dimensions of the availabl space for the treatment plant?
    length_treatment_plant = fields.Float('Length')
    width_treatment_plant = fields.Float('Width')
    height_treatment_plant = fields.Float('Height')
    gradient_treatment_plant = fields.Float('Gradient')
    wind_load = fields.Char('What is the specified wind load?')
    specific_governmental = fields.Boolean('Are there specific governmental standards')
    specific_material = fields.Boolean('Are there specific materials preferred for construction?')
    any_data_available = fields.Boolean('Are there any data available regarding the soil composition, ground water level, etc.?')
    flange_type = fields.Selection([
        ('din', 'DIN'),
        ('ansi', 'ANSI'),
        ('jis', 'JIS')
    ], string='Which flange types are required?')
    is_seasonal_deviations = fields.Boolean('Are there seasonal deviations within the production process(es)?')
    is_height_limitation = fields.Boolean('Are there height limitation?')
    is_area_limitation = fields.Boolean('Are there area limitations?')
    is_limitation_to_transport_tanks = fields.Boolean('Are there any limitations to transport tanks, orreactors, from GLS  to the customer.')
    transport_id = fields.Many2one('transport.survey', string='Transport by')

    # Electrical Condition On Location
    voltage = fields.Float('What is the available voltage?')
    frequency = fields.Float('What is the available frequency?')
    available_power = fields.Float('What is the available power?')
    power = fields.Float('Distance between power supply and treatment plant')
    source_power = fields.Selection([
        ('pln', 'PLN'),
        ('own', 'Own Power Plant')
    ], string='Source of power supply')

    # Description of the Area
    description_area = fields.Html('Description of the Area')
    is_attachment = fields.Boolean('Drawings available?')
    attachment_area = fields.Binary('Attachment Area')

    # Description of the Existing Water/Wastewater Treatment
    description_existing = fields.Html('Description of the Area')
    is_attachment_existing = fields.Boolean('Drawings available?')
    attachment_area_existing = fields.Binary('Attachment Area')

    # Additional Remarks or Documentations (Pictures, Sketches)
    description_remarks = fields.Html('Additional Remarks or Documentations (Pictures, Sketches)')
    attachment_remarks = fields.Binary('Attachment')

    # CNA Report

    # General Details

    facility_name = fields.Char(string="Facility Name")
    owning_company = fields.Char(string="Owning Company/Group")
    address = fields.Char(string="Address")
    contact_person = fields.Char("Contact Person")
    telephone = fields.Char("Telephone")
    email = fields.Char("E-mail")

    # Type of Business

    business_type_cna = fields.Many2one('business.type', string="Type of Business")

    # Client Category

    client_category = fields.Selection([
        ('high', 'High End'),
        ('mid', 'Mid End'),
        ('low', 'Low End(Budget)')
    ])

    # Project Status

    project_status = fields.Many2one('project.status', 'Project Status')

    # Project Scheme

    project_scheme = fields.Many2one('project.scheme', 'Project Scheme')

    # Timeline

    proposal_submission = fields.Char('Proposal Submission')
    construction_period = fields.Char('Construction Start Period')

    # Budget/Price Limitation

    budget_limitation = fields.Char('Budget/Price Limitation')

    # Competitors

    competitors = fields.Char('Competitors')

    # Other issue / Other Concern

    other_issue = fields.Binary('Other Issue/Other Concern')

    change_stage_time = fields.Datetime('Change Stage Time',store=True)
    duration_change_stage = fields.Char(string='Duration')
    
    @api.onchange('stage_id')
    def _onchange_stagescrm_id(self):
        for i in self:
            i.change_stage_time = fields.datetime.now()
         

    # @api.depends('change_stage_time')
    def _compute_duration_change_stage(self):
        now = fields.datetime.now()
        for i in self:
            if i.change_stage_time:
                diff = relativedelta.relativedelta(i.change_stage_time, now)
                years = diff.years
                months = diff.months
                days = diff.days
                hours = diff.hours
                minutes = diff.minutes
                if years > 0:
                    i.duration_change_stage = str(years) + " Year " + str(months) + " month " + str(days) + " day" + str(hours) + " jam " + str(minutes) + " menit"
                elif months > 0:
                    i.duration_change_stage = str(months) + " Month " + str(days) + " day " + str(hours) + " hour " + str(minutes) + " menit"
                elif days > 0:
                    i.duration_change_stage = str(days) + " Days " + str(hours) + " hours " + str(minutes) + " minutes"
                elif hours > 0:
                    i.duration_change_stage = str(hours) + " Hours " + str(minutes) + " minutes"
                else:
                    i.duration_change_stage =str(minutes) + " Minutes " + str(diff.seconds) + " seconds"
            else:
                i.duration_change_stage = 'The changes stage time is not defined!'

    def write(self, vals):
        for i in self:
            default_stage = self.env["crm.stage"].search([],order='sequence asc',limit=1)
            before = self.stage_id
            if default_stage != before and vals.get("stage_id"):
                after = vals.get("stage_id")
                if not i.env.user.employee_id:
                    raise ValidationError("Your account need relateion to employee!")
                elif not i.user_id:
                    raise ValidationError("Salesperson is not define.")
                elif not i.user_id.employee_id:
                    raise ValidationError("Salesperson doesn't have employee!")
                elif not i.user_id.employee_id.parent_id:
                    raise ValidationError("Salesperson manager's in employee is not define.")
                else:
                    if i.user_id.employee_id.parent_id.id != i.env.user.employee_id.id:
                        raise ValidationError("Only salesperson manager's can change the stage!")
        return super(CrmLead, self).write(vals)
