import '../models/user_views.dart';

class ViewCategoriesService {
  static final ViewCategoriesService _instance = ViewCategoriesService._internal();
  factory ViewCategoriesService() => _instance;
  ViewCategoriesService._internal();

  // Predefined categories with their issues
  List<IssueCategory> getPredefinedCategories() {
    return [
      _createGeopoliticsCategory(),
      _createEconomicsCategory(),
      _createSocialIssuesCategory(),
      _createTechScienceCategory(),
      _createHealthCategory(),
      _createSportsCategory(),
    ];
  }

  // Helper method to get subcategories for a category
  List<Subcategory> getSubcategoriesForCategory(String categoryId) {
    final category = getCategoryById(categoryId);
    if (category == null) return [];

    // Group issues by subcategory
    final Map<String, List<IssueView>> subcategoryGroups = {};
    
    for (final issue in category.issues) {
      final subcategoryName = issue.subcategory ?? 'General';
      if (!subcategoryGroups.containsKey(subcategoryName)) {
        subcategoryGroups[subcategoryName] = [];
      }
      subcategoryGroups[subcategoryName]!.add(issue);
    }

    // Convert to Subcategory objects
    return subcategoryGroups.entries.map((entry) {
      return Subcategory(
        name: entry.key,
        displayName: _getSubcategoryDisplayName(entry.key),
        issues: entry.value,
      );
    }).toList();
  }

  // Helper method to get display names for subcategories
  String _getSubcategoryDisplayName(String subcategoryName) {
    switch (subcategoryName) {
      case 'conflicts': return 'Conflicts';
      case 'major_powers': return 'Major Powers';
      case 'territorial_disputes': return 'Territorial Disputes';
      case 'alliances_organizations': return 'Alliances & Organizations';
      case 'nuclear_security': return 'Nuclear & Security';
      case 'trade_economic_relations': return 'Trade & Economic Relations';
      case 'central_banks': return 'Central Banks';
      case 'monetary_policy': return 'Monetary Policy';
      case 'stock_markets': return 'Stock Markets';
      case 'major_companies': return 'Major Companies';
      case 'cryptocurrency': return 'Cryptocurrency';
      case 'commodities': return 'Commodities';
      case 'economic_indicators': return 'Economic Indicators';
      case 'economic_policies': return 'Economic Policies';
      case 'climate_environment': return 'Climate & Environment';
      case 'healthcare': return 'Healthcare';
      case 'education': return 'Education';
      case 'criminal_justice': return 'Criminal Justice';
      case 'civil_rights': return 'Civil Rights';
      case 'immigration': return 'Immigration';
      case 'labor_workers': return 'Labor & Workers';
      case 'major_tech_companies': return 'Major Tech Companies';
      case 'ai_technology': return 'AI & Technology';
      case 'space_innovation': return 'Space & Innovation';
      case 'scientific_research': return 'Scientific Research';
      case 'social_media_platforms': return 'Social Media & Platforms';
      case 'vaccination': return 'Vaccination';
      case 'diet_nutrition': return 'Diet & Nutrition';
      case 'exercise_fitness': return 'Exercise & Fitness';
      case 'medical_treatments': return 'Medical Treatments';
      case 'public_health': return 'Public Health';
      case 'major_leagues': return 'Major Leagues';
      case 'major_events': return 'Major Events';
      case 'sports_issues': return 'Sports Issues';
      default: return subcategoryName;
    }
  }

  // Geopolitics Category - Organized by subcategories
  IssueCategory _createGeopoliticsCategory() {
    return IssueCategory(
      categoryId: 'geopolitics',
      categoryName: 'Geopolitics',
      description: 'International relations and global conflicts',
      icon: '🌍',
      issues: [
        // === CONFLICTS ===
        IssueView(
          issueId: 'conflict_israel_palestine',
          issueName: 'Israel-Palestine Conflict',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'conflicts',
        ),
        IssueView(
          issueId: 'conflict_russia_ukraine',
          issueName: 'Russia-Ukraine War',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'conflicts',
        ),
        IssueView(
          issueId: 'conflict_syria',
          issueName: 'Syrian Civil War',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'conflicts',
        ),
        IssueView(
          issueId: 'conflict_yemen',
          issueName: 'Yemen Civil War',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'conflicts',
        ),
        IssueView(
          issueId: 'conflict_ethiopia',
          issueName: 'Ethiopian Civil War',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'conflicts',
        ),
        
        // === MAJOR POWERS ===
        IssueView(
          issueId: 'power_china',
          issueName: 'China\'s Global Influence',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'major_powers',
        ),
        IssueView(
          issueId: 'power_russia',
          issueName: 'Russia\'s Foreign Policy',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'major_powers',
        ),
        IssueView(
          issueId: 'power_iran',
          issueName: 'Iran\'s Regional Role',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'major_powers',
        ),
        IssueView(
          issueId: 'power_turkey',
          issueName: 'Turkey\'s Foreign Policy',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'major_powers',
        ),
        IssueView(
          issueId: 'power_india',
          issueName: 'India\'s Global Role',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'major_powers',
        ),
        
        // === TERRITORIAL DISPUTES ===
        IssueView(
          issueId: 'dispute_china_taiwan',
          issueName: 'China-Taiwan Relations',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'territorial_disputes',
        ),
        IssueView(
          issueId: 'dispute_south_china_sea',
          issueName: 'South China Sea Dispute',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'territorial_disputes',
        ),
        IssueView(
          issueId: 'dispute_kashmir',
          issueName: 'Kashmir Dispute',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'territorial_disputes',
        ),
        IssueView(
          issueId: 'dispute_ukraine_crimea',
          issueName: 'Crimea Annexation',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'territorial_disputes',
        ),
        
        // === ALLIANCES & ORGANIZATIONS ===
        IssueView(
          issueId: 'alliance_nato',
          issueName: 'NATO Expansion',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'alliances_organizations',
        ),
        IssueView(
          issueId: 'alliance_quad',
          issueName: 'Quad Alliance (US, Japan, India, Australia)',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'alliances_organizations',
        ),
        IssueView(
          issueId: 'alliance_brics',
          issueName: 'BRICS Alliance',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'alliances_organizations',
        ),
        IssueView(
          issueId: 'alliance_eu',
          issueName: 'European Union Unity',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'alliances_organizations',
        ),
        
        // === NUCLEAR & SECURITY ===
        IssueView(
          issueId: 'nuclear_iran',
          issueName: 'Iran Nuclear Program',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'nuclear_security',
        ),
        IssueView(
          issueId: 'nuclear_north_korea',
          issueName: 'North Korea Nuclear Program',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'nuclear_security',
        ),
        IssueView(
          issueId: 'nuclear_proliferation',
          issueName: 'Nuclear Proliferation',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'nuclear_security',
        ),
        
        // === TRADE & ECONOMIC RELATIONS ===
        IssueView(
          issueId: 'trade_us_china',
          issueName: 'US-China Trade Relations',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'trade_economic_relations',
        ),
        IssueView(
          issueId: 'trade_globalization',
          issueName: 'Globalization & Trade Wars',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'trade_economic_relations',
        ),
        IssueView(
          issueId: 'trade_sanctions',
          issueName: 'Economic Sanctions',
          categoryId: 'geopolitics',
          categoryName: 'Geopolitics',
          subcategory: 'trade_economic_relations',
        ),
      ],
    );
  }

  // Economics Category - Organized by subcategories
  IssueCategory _createEconomicsCategory() {
    return IssueCategory(
      categoryId: 'economics',
      categoryName: 'Economics',
      description: 'Financial markets and economic policies',
      icon: '💰',
      issues: [
        // === CENTRAL BANKS ===
        IssueView(
          issueId: 'central_bank_fed',
          issueName: 'Federal Reserve Policy',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'central_banks',
        ),
        IssueView(
          issueId: 'central_bank_ecb',
          issueName: 'European Central Bank',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'central_banks',
        ),
        IssueView(
          issueId: 'central_bank_boj',
          issueName: 'Bank of Japan',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'central_banks',
        ),
        IssueView(
          issueId: 'central_bank_pboc',
          issueName: 'People\'s Bank of China',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'central_banks',
        ),
        
        // === MONETARY POLICY ===
        IssueView(
          issueId: 'rates_inflation',
          issueName: 'Inflation & Interest Rates',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'monetary_policy',
        ),
        IssueView(
          issueId: 'rates_quantitative_easing',
          issueName: 'Quantitative Easing',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'monetary_policy',
        ),
        IssueView(
          issueId: 'rates_yield_curve',
          issueName: 'Yield Curve Inversion',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'monetary_policy',
        ),
        
        // === STOCK MARKETS ===
        IssueView(
          issueId: 'stocks_sp500',
          issueName: 'S&P 500 Index',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'stock_markets',
        ),
        IssueView(
          issueId: 'stocks_nasdaq',
          issueName: 'NASDAQ Composite',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'stock_markets',
        ),
        IssueView(
          issueId: 'stocks_dow',
          issueName: 'Dow Jones Industrial Average',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'stock_markets',
        ),
        IssueView(
          issueId: 'stocks_ftse',
          issueName: 'FTSE 100 (UK)',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'stock_markets',
        ),
        IssueView(
          issueId: 'stocks_nikkei',
          issueName: 'Nikkei 225 (Japan)',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'stock_markets',
        ),
        
        // === MAJOR COMPANIES ===
        IssueView(
          issueId: 'company_apple',
          issueName: 'Apple Inc.',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'major_companies',
        ),
        IssueView(
          issueId: 'company_microsoft',
          issueName: 'Microsoft Corporation',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'major_companies',
        ),
        IssueView(
          issueId: 'company_google',
          issueName: 'Alphabet (Google)',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'major_companies',
        ),
        IssueView(
          issueId: 'company_amazon',
          issueName: 'Amazon.com',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'major_companies',
        ),
        IssueView(
          issueId: 'company_tesla',
          issueName: 'Tesla Inc.',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'major_companies',
        ),
        IssueView(
          issueId: 'company_berkshire',
          issueName: 'Berkshire Hathaway',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'major_companies',
        ),
        
        // === CRYPTOCURRENCY ===
        IssueView(
          issueId: 'crypto_bitcoin',
          issueName: 'Bitcoin',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'cryptocurrency',
        ),
        IssueView(
          issueId: 'crypto_ethereum',
          issueName: 'Ethereum',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'cryptocurrency',
        ),
        IssueView(
          issueId: 'crypto_regulation',
          issueName: 'Cryptocurrency Regulation',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'cryptocurrency',
        ),
        IssueView(
          issueId: 'crypto_central_bank_digital',
          issueName: 'Central Bank Digital Currencies',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'cryptocurrency',
        ),
        
        // === COMMODITIES ===
        IssueView(
          issueId: 'commodity_oil',
          issueName: 'Oil Prices',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'commodities',
        ),
        IssueView(
          issueId: 'commodity_gold',
          issueName: 'Gold Prices',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'commodities',
        ),
        IssueView(
          issueId: 'commodity_silver',
          issueName: 'Silver Prices',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'commodities',
        ),
        
        // === ECONOMIC INDICATORS ===
        IssueView(
          issueId: 'indicator_gdp',
          issueName: 'GDP Growth',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'economic_indicators',
        ),
        IssueView(
          issueId: 'indicator_unemployment',
          issueName: 'Unemployment Rate',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'economic_indicators',
        ),
        IssueView(
          issueId: 'indicator_housing_market',
          issueName: 'Housing Market',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'economic_indicators',
        ),
        
        // === ECONOMIC POLICIES ===
        IssueView(
          issueId: 'policy_tax',
          issueName: 'Tax Policy',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'economic_policies',
        ),
        IssueView(
          issueId: 'policy_fiscal',
          issueName: 'Fiscal Policy',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'economic_policies',
        ),
        IssueView(
          issueId: 'policy_trade',
          issueName: 'Trade Policy',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'economic_policies',
        ),
        IssueView(
          issueId: 'policy_debt',
          issueName: 'National Debt',
          categoryId: 'economics',
          categoryName: 'Economics',
          subcategory: 'economic_policies',
        ),
      ],
    );
  }

  // Social Issues Category - Organized by subcategories
  IssueCategory _createSocialIssuesCategory() {
    return IssueCategory(
      categoryId: 'social_issues',
      categoryName: 'Social Issues',
      description: 'Major social and policy debates',
      icon: '🤝',
      issues: [
        // === CLIMATE & ENVIRONMENT ===
        IssueView(
          issueId: 'climate_global_warming',
          issueName: 'Global Warming',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'climate_environment',
        ),
        IssueView(
          issueId: 'climate_carbon_emissions',
          issueName: 'Carbon Emissions',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'climate_environment',
        ),
        IssueView(
          issueId: 'climate_renewable_energy',
          issueName: 'Renewable Energy',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'climate_environment',
        ),
        IssueView(
          issueId: 'climate_fossil_fuels',
          issueName: 'Fossil Fuel Industry',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'climate_environment',
        ),
        IssueView(
          issueId: 'climate_extreme_weather',
          issueName: 'Extreme Weather Events',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'climate_environment',
        ),
        
        // === HEALTHCARE ===
        IssueView(
          issueId: 'healthcare_access',
          issueName: 'Healthcare Access',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'healthcare',
        ),
        IssueView(
          issueId: 'healthcare_medicare',
          issueName: 'Medicare & Medicaid',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'healthcare',
        ),
        IssueView(
          issueId: 'healthcare_obamacare',
          issueName: 'Affordable Care Act',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'healthcare',
        ),
        IssueView(
          issueId: 'healthcare_abortion',
          issueName: 'Abortion Rights',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'healthcare',
        ),
        
        // === EDUCATION ===
        IssueView(
          issueId: 'education_funding',
          issueName: 'Education Funding',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'education',
        ),
        IssueView(
          issueId: 'education_student_loans',
          issueName: 'Student Loan Debt',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'education',
        ),
        IssueView(
          issueId: 'education_college_admissions',
          issueName: 'College Admissions',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'education',
        ),
        IssueView(
          issueId: 'education_public_schools',
          issueName: 'Public School System',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'education',
        ),
        IssueView(
          issueId: 'education_charter_schools',
          issueName: 'Charter Schools',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'education',
        ),
        
        // === CRIMINAL JUSTICE ===
        IssueView(
          issueId: 'justice_police_reform',
          issueName: 'Police Reform',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'criminal_justice',
        ),
        IssueView(
          issueId: 'justice_mass_incarceration',
          issueName: 'Mass Incarceration',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'criminal_justice',
        ),
        IssueView(
          issueId: 'justice_death_penalty',
          issueName: 'Death Penalty',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'criminal_justice',
        ),
        IssueView(
          issueId: 'justice_gun_control',
          issueName: 'Gun Control',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'criminal_justice',
        ),
        IssueView(
          issueId: 'justice_drug_policy',
          issueName: 'Drug Policy',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'criminal_justice',
        ),
        
        // === CIVIL RIGHTS ===
        IssueView(
          issueId: 'rights_racial_justice',
          issueName: 'Racial Justice',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'civil_rights',
        ),
        IssueView(
          issueId: 'rights_lgbtq',
          issueName: 'LGBTQ+ Rights',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'civil_rights',
        ),
        IssueView(
          issueId: 'rights_women',
          issueName: 'Women\'s Rights',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'civil_rights',
        ),
        IssueView(
          issueId: 'rights_voting',
          issueName: 'Voting Rights',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'civil_rights',
        ),
        IssueView(
          issueId: 'rights_free_speech',
          issueName: 'Free Speech',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'civil_rights',
        ),
        
        // === IMMIGRATION ===
        IssueView(
          issueId: 'immigration_policy',
          issueName: 'Immigration Policy',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'immigration',
        ),
        IssueView(
          issueId: 'immigration_border',
          issueName: 'Border Security',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'immigration',
        ),
        IssueView(
          issueId: 'immigration_daca',
          issueName: 'DACA Program',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'immigration',
        ),
        IssueView(
          issueId: 'immigration_refugees',
          issueName: 'Refugee Policy',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'immigration',
        ),
        
        // === LABOR & WORKERS ===
        IssueView(
          issueId: 'labor_minimum_wage',
          issueName: 'Minimum Wage',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'labor_workers',
        ),
        IssueView(
          issueId: 'labor_unions',
          issueName: 'Labor Unions',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'labor_workers',
        ),
        IssueView(
          issueId: 'labor_automation',
          issueName: 'Automation & Jobs',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'labor_workers',
        ),
        IssueView(
          issueId: 'labor_income_inequality',
          issueName: 'Income Inequality',
          categoryId: 'social_issues',
          categoryName: 'Social Issues',
          subcategory: 'labor_workers',
        ),
      ],
    );
  }

  // Tech & Science Category - Combined and focused
  IssueCategory _createTechScienceCategory() {
    return IssueCategory(
      categoryId: 'tech_science',
      categoryName: 'Tech & Science',
      description: 'Technology, science, and innovation',
      icon: '🔬',
      issues: [
        // === MAJOR TECH COMPANIES ===
        IssueView(
          issueId: 'tech_apple',
          issueName: 'Apple',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'major_tech_companies',
        ),
        IssueView(
          issueId: 'tech_google',
          issueName: 'Google',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'major_tech_companies',
        ),
        IssueView(
          issueId: 'tech_microsoft',
          issueName: 'Microsoft',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'major_tech_companies',
        ),
        IssueView(
          issueId: 'tech_amazon',
          issueName: 'Amazon',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'major_tech_companies',
        ),
        IssueView(
          issueId: 'tech_meta',
          issueName: 'Meta (Facebook)',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'major_tech_companies',
        ),
        
        // === AI & TECHNOLOGY ===
        IssueView(
          issueId: 'ai_chatgpt',
          issueName: 'ChatGPT & AI Chatbots',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'ai_technology',
        ),
        IssueView(
          issueId: 'ai_automation',
          issueName: 'AI Automation & Jobs',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'ai_technology',
        ),
        IssueView(
          issueId: 'ai_self_driving',
          issueName: 'Self-Driving Cars',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'ai_technology',
        ),
        IssueView(
          issueId: 'ai_ethics',
          issueName: 'AI Ethics & Regulation',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'ai_technology',
        ),
        
        // === SPACE & INNOVATION ===
        IssueView(
          issueId: 'space_spacex',
          issueName: 'SpaceX',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'space_innovation',
        ),
        IssueView(
          issueId: 'space_nasa',
          issueName: 'NASA Missions',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'space_innovation',
        ),
        IssueView(
          issueId: 'space_mars',
          issueName: 'Mars Exploration',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'space_innovation',
        ),
        
        // === SCIENTIFIC RESEARCH ===
        IssueView(
          issueId: 'science_climate_research',
          issueName: 'Climate Science',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'scientific_research',
        ),
        IssueView(
          issueId: 'science_medical_research',
          issueName: 'Medical Research',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'scientific_research',
        ),
        IssueView(
          issueId: 'science_quantum_computing',
          issueName: 'Quantum Computing',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'scientific_research',
        ),
        
        // === SOCIAL MEDIA & PLATFORMS ===
        IssueView(
          issueId: 'social_tiktok',
          issueName: 'TikTok',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'social_media_platforms',
        ),
        IssueView(
          issueId: 'social_twitter',
          issueName: 'Twitter/X',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'social_media_platforms',
        ),
        IssueView(
          issueId: 'social_youtube',
          issueName: 'YouTube',
          categoryId: 'tech_science',
          categoryName: 'Tech & Science',
          subcategory: 'social_media_platforms',
        ),
      ],
    );
  }

  // Health Category - Focused on non-controversial topics
  IssueCategory _createHealthCategory() {
    return IssueCategory(
      categoryId: 'health',
      categoryName: 'Health',
      description: 'Health, wellness, and medical topics',
      icon: '🏥',
      issues: [
        // === VACCINATION ===
        IssueView(
          issueId: 'health_vaccination',
          issueName: 'Vaccination Programs',
          categoryId: 'health',
          categoryName: 'Health',
          subcategory: 'vaccination',
        ),
        IssueView(
          issueId: 'health_vaccine_safety',
          issueName: 'Vaccine Safety',
          categoryId: 'health',
          categoryName: 'Health',
          subcategory: 'vaccination',
        ),
        
        // === DIET & NUTRITION ===
        IssueView(
          issueId: 'health_vegetarian_diet',
          issueName: 'Vegetarian Diets',
          categoryId: 'health',
          categoryName: 'Health',
          subcategory: 'diet_nutrition',
        ),
        IssueView(
          issueId: 'health_vegan_diet',
          issueName: 'Vegan Diets',
          categoryId: 'health',
          categoryName: 'Health',
          subcategory: 'diet_nutrition',
        ),
        IssueView(
          issueId: 'health_keto_diet',
          issueName: 'Keto Diet',
          categoryId: 'health',
          categoryName: 'Health',
          subcategory: 'diet_nutrition',
        ),
        IssueView(
          issueId: 'health_organic_food',
          issueName: 'Organic Food',
          categoryId: 'health',
          categoryName: 'Health',
          subcategory: 'diet_nutrition',
        ),
        
        // === EXERCISE & FITNESS ===
        IssueView(
          issueId: 'health_exercise',
          issueName: 'Exercise & Fitness',
          categoryId: 'health',
          categoryName: 'Health',
          subcategory: 'exercise_fitness',
        ),
        IssueView(
          issueId: 'health_yoga',
          issueName: 'Yoga & Meditation',
          categoryId: 'health',
          categoryName: 'Health',
          subcategory: 'exercise_fitness',
        ),
        
        // === MEDICAL TREATMENTS ===
        IssueView(
          issueId: 'health_alternative_medicine',
          issueName: 'Alternative Medicine',
          categoryId: 'health',
          categoryName: 'Health',
          subcategory: 'medical_treatments',
        ),
        IssueView(
          issueId: 'health_pharmaceuticals',
          issueName: 'Pharmaceutical Industry',
          categoryId: 'health',
          categoryName: 'Health',
          subcategory: 'medical_treatments',
        ),
        
        // === PUBLIC HEALTH ===
        IssueView(
          issueId: 'health_obesity',
          issueName: 'Obesity Epidemic',
          categoryId: 'health',
          categoryName: 'Health',
          subcategory: 'public_health',
        ),
        IssueView(
          issueId: 'health_antibiotics',
          issueName: 'Antibiotic Resistance',
          categoryId: 'health',
          categoryName: 'Health',
          subcategory: 'public_health',
        ),
        IssueView(
          issueId: 'health_healthcare_systems',
          issueName: 'Healthcare Systems',
          categoryId: 'health',
          categoryName: 'Health',
          subcategory: 'public_health',
        ),
      ],
    );
  }

  // Sports Category - Focused on leagues and sports (LAST)
  IssueCategory _createSportsCategory() {
    return IssueCategory(
      categoryId: 'sports',
      categoryName: 'Sports',
      description: 'Professional sports and leagues',
      icon: '⚽',
      issues: [
        // === MAJOR LEAGUES ===
        IssueView(
          issueId: 'league_nfl',
          issueName: 'NFL (American Football)',
          categoryId: 'sports',
          categoryName: 'Sports',
          subcategory: 'major_leagues',
        ),
        IssueView(
          issueId: 'league_nba',
          issueName: 'NBA (Basketball)',
          categoryId: 'sports',
          categoryName: 'Sports',
          subcategory: 'major_leagues',
        ),
        IssueView(
          issueId: 'league_mlb',
          issueName: 'MLB (Baseball)',
          categoryId: 'sports',
          categoryName: 'Sports',
          subcategory: 'major_leagues',
        ),
        IssueView(
          issueId: 'league_nhl',
          issueName: 'NHL (Hockey)',
          categoryId: 'sports',
          categoryName: 'Sports',
          subcategory: 'major_leagues',
        ),
        IssueView(
          issueId: 'league_premier_league',
          issueName: 'Premier League (Soccer)',
          categoryId: 'sports',
          categoryName: 'Sports',
          subcategory: 'major_leagues',
        ),
        IssueView(
          issueId: 'league_la_liga',
          issueName: 'La Liga (Soccer)',
          categoryId: 'sports',
          categoryName: 'Sports',
          subcategory: 'major_leagues',
        ),
        IssueView(
          issueId: 'league_serie_a',
          issueName: 'Serie A (Soccer)',
          categoryId: 'sports',
          categoryName: 'Sports',
          subcategory: 'major_leagues',
        ),
        IssueView(
          issueId: 'league_bundesliga',
          issueName: 'Bundesliga (Soccer)',
          categoryId: 'sports',
          categoryName: 'Sports',
          subcategory: 'major_leagues',
        ),
        
        // === MAJOR EVENTS ===
        IssueView(
          issueId: 'event_world_cup',
          issueName: 'FIFA World Cup',
          categoryId: 'sports',
          categoryName: 'Sports',
          subcategory: 'major_events',
        ),
        IssueView(
          issueId: 'event_olympics',
          issueName: 'Olympic Games',
          categoryId: 'sports',
          categoryName: 'Sports',
          subcategory: 'major_events',
        ),
        IssueView(
          issueId: 'event_super_bowl',
          issueName: 'Super Bowl',
          categoryId: 'sports',
          categoryName: 'Sports',
          subcategory: 'major_events',
        ),
        
        // === SPORTS ISSUES ===
        IssueView(
          issueId: 'sports_doping',
          issueName: 'Doping in Sports',
          categoryId: 'sports',
          categoryName: 'Sports',
          subcategory: 'sports_issues',
        ),
        IssueView(
          issueId: 'sports_concussions',
          issueName: 'Concussions & Player Safety',
          categoryId: 'sports',
          categoryName: 'Sports',
          subcategory: 'sports_issues',
        ),
        IssueView(
          issueId: 'sports_esports',
          issueName: 'Esports',
          categoryId: 'sports',
          categoryName: 'Sports',
          subcategory: 'sports_issues',
        ),
      ],
    );
  }

  // Get category by ID
  IssueCategory? getCategoryById(String categoryId) {
    try {
      return getPredefinedCategories().firstWhere((category) => category.categoryId == categoryId);
    } catch (e) {
      return null;
    }
  }

  // Get issue by ID
  IssueView? getIssueById(String issueId) {
    for (final category in getPredefinedCategories()) {
      try {
        return category.issues.firstWhere((issue) => issue.issueId == issueId);
      } catch (e) {
        continue;
      }
    }
    return null;
  }

  // Get all issues
  List<IssueView> getAllIssues() {
    return getPredefinedCategories()
        .expand((category) => category.issues)
        .toList();
  }

  // Search issues by name
  List<IssueView> searchIssues(String query) {
    final lowercaseQuery = query.toLowerCase();
    return getAllIssues()
        .where((issue) => issue.issueName.toLowerCase().contains(lowercaseQuery))
        .toList();
  }

  // Get popular issues (for onboarding) - focused on major topics
  List<IssueView> getPopularIssues() {
    return [
      getIssueById('conflict_israel_palestine')!,
      getIssueById('conflict_russia_ukraine')!,
      getIssueById('power_china')!,
      getIssueById('central_bank_fed')!,
      getIssueById('rates_inflation')!,
      getIssueById('climate_global_warming')!,
      getIssueById('healthcare_access')!,
      getIssueById('ai_chatgpt')!,
    ];
  }
} 