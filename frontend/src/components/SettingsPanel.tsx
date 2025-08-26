import React, { useState, useEffect } from 'react';
import { Settings, Shield, Eye, Sliders, Save, RotateCcw } from 'lucide-react';

interface PolicySettings {
  PERSON: string;
  PHONE: string;
  EMAIL: string;
  AADHAAR: string;
  PAN: string;
  IFSC: string;
  ACCOUNT_NO: string;
  SIGNATURE: string;
  FACE: string;
  STAMP: string;
  DATE: string;
  ORG: string;
}

interface ThresholdSettings {
  ocr_confidence: number;
  ner_confidence: number;
  face_threshold: number;
  signature_threshold: number;
  padding_px: number;
}

const SettingsPanel: React.FC = () => {
  const [policies, setPolicies] = useState<PolicySettings>({
    PERSON: 'mask',
    PHONE: 'replace',
    EMAIL: 'mask',
    AADHAAR: 'mask',
    PAN: 'mask',
    IFSC: 'mask',
    ACCOUNT_NO: 'mask',
    SIGNATURE: 'blur',
    FACE: 'blur',
    STAMP: 'mask',
    DATE: 'mask',
    ORG: 'mask',
  });

  const [thresholds, setThresholds] = useState<ThresholdSettings>({
    ocr_confidence: 0.5,
    ner_confidence: 0.6,
    face_threshold: 0.5,
    signature_threshold: 0.35,
    padding_px: 4,
  });

  const redactionMethods = [
    { value: 'mask', label: 'Black Box', description: 'Cover with black rectangle' },
    { value: 'blur', label: 'Blur', description: 'Apply Gaussian blur effect' },
    { value: 'replace', label: 'Replace', description: 'Replace with placeholder text' },
    { value: 'remove', label: 'Remove', description: 'Remove completely' },
  ];

  const piiTypes = [
    { key: 'PERSON', label: 'Person Names', icon: '👤' },
    { key: 'PHONE', label: 'Phone Numbers', icon: '📞' },
    { key: 'EMAIL', label: 'Email Addresses', icon: '📧' },
    { key: 'AADHAAR', label: 'Aadhaar Numbers', icon: '🆔' },
    { key: 'PAN', label: 'PAN Numbers', icon: '💳' },
    { key: 'IFSC', label: 'IFSC Codes', icon: '🏦' },
    { key: 'ACCOUNT_NO', label: 'Account Numbers', icon: '💰' },
    { key: 'SIGNATURE', label: 'Signatures', icon: '✍️' },
    { key: 'FACE', label: 'Faces', icon: '😊' },
    { key: 'STAMP', label: 'Stamps/Seals', icon: '🔖' },
    { key: 'DATE', label: 'Dates', icon: '📅' },
    { key: 'ORG', label: 'Organizations', icon: '🏢' },
  ];

  const handlePolicyChange = (piiType: keyof PolicySettings, method: string) => {
    setPolicies(prev => ({ ...prev, [piiType]: method }));
  };

  const handleThresholdChange = (key: keyof ThresholdSettings, value: number) => {
    setThresholds(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    // In a real app, this would save to backend or localStorage
    console.log('Settings saved:', { policies, thresholds });
  };

  const handleReset = () => {
    // Reset to defaults
    setPolicies({
      PERSON: 'mask',
      PHONE: 'replace',
      EMAIL: 'mask',
      AADHAAR: 'mask',
      PAN: 'mask',
      IFSC: 'mask',
      ACCOUNT_NO: 'mask',
      SIGNATURE: 'blur',
      FACE: 'blur',
      STAMP: 'mask',
      DATE: 'mask',
      ORG: 'mask',
    });
    
    setThresholds({
      ocr_confidence: 0.5,
      ner_confidence: 0.6,
      face_threshold: 0.5,
      signature_threshold: 0.35,
      padding_px: 4,
    });
  };

  const getMethodColor = (method: string) => {
    switch (method) {
      case 'mask': return 'bg-gray-600';
      case 'blur': return 'bg-blue-600';
      case 'replace': return 'bg-green-600';
      case 'remove': return 'bg-red-600';
      default: return 'bg-gray-600';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="card">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-primary-100 rounded-full">
            <Settings className="h-6 w-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Redaction Settings</h1>
            <p className="text-gray-600">Configure how different types of PII should be handled</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Redaction Policies */}
        <div className="card">
          <div className="flex items-center space-x-2 mb-6">
            <Shield className="h-5 w-5 text-primary-600" />
            <h2 className="text-xl font-semibold text-gray-900">Redaction Policies</h2>
          </div>

          <div className="space-y-4">
            {piiTypes.map(({ key, label, icon }) => (
              <div key={key} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">{icon}</span>
                  <div>
                    <p className="font-medium text-gray-900">{label}</p>
                    <p className="text-xs text-gray-500">{key}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <select
                    value={policies[key as keyof PolicySettings]}
                    onChange={(e) => handlePolicyChange(key as keyof PolicySettings, e.target.value)}
                    className="input text-sm py-1 px-2 min-w-[100px]"
                  >
                    {redactionMethods.map(method => (
                      <option key={method.value} value={method.value}>
                        {method.label}
                      </option>
                    ))}
                  </select>
                  <div
                    className={`w-3 h-3 rounded-full ${getMethodColor(policies[key as keyof PolicySettings])}`}
                    title={redactionMethods.find(m => m.value === policies[key as keyof PolicySettings])?.description}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Detection Thresholds */}
        <div className="space-y-6">
          <div className="card">
            <div className="flex items-center space-x-2 mb-6">
              <Sliders className="h-5 w-5 text-primary-600" />
              <h2 className="text-xl font-semibold text-gray-900">Detection Thresholds</h2>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  OCR Confidence Threshold
                  <span className="text-gray-500 ml-2">({thresholds.ocr_confidence})</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={thresholds.ocr_confidence}
                  onChange={(e) => handleThresholdChange('ocr_confidence', parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Low (0.0)</span>
                  <span>High (1.0)</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Text PII Confidence Threshold
                  <span className="text-gray-500 ml-2">({thresholds.ner_confidence})</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={thresholds.ner_confidence}
                  onChange={(e) => handleThresholdChange('ner_confidence', parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Sensitive (0.0)</span>
                  <span>Strict (1.0)</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Face Detection Threshold
                  <span className="text-gray-500 ml-2">({thresholds.face_threshold})</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={thresholds.face_threshold}
                  onChange={(e) => handleThresholdChange('face_threshold', parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Signature Detection Threshold
                  <span className="text-gray-500 ml-2">({thresholds.signature_threshold})</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={thresholds.signature_threshold}
                  onChange={(e) => handleThresholdChange('signature_threshold', parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Redaction Padding (pixels)
                  <span className="text-gray-500 ml-2">({thresholds.padding_px}px)</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="20"
                  step="1"
                  value={thresholds.padding_px}
                  onChange={(e) => handleThresholdChange('padding_px', parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>No padding (0px)</span>
                  <span>Max padding (20px)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Privacy Notice */}
          <div className="card bg-primary-50 border-primary-200">
            <div className="flex items-start space-x-3">
              <Shield className="h-5 w-5 text-primary-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-primary-900 text-sm">Privacy Notice</h3>
                <p className="text-primary-700 text-xs mt-1">
                  All settings are applied locally on your device. No configuration data
                  is sent to external servers. Adjust thresholds based on your privacy requirements.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end space-x-4">
        <button
          onClick={handleReset}
          className="btn-secondary"
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          Reset to Defaults
        </button>
        <button
          onClick={handleSave}
          className="btn-primary"
        >
          <Save className="h-4 w-4 mr-2" />
          Save Settings
        </button>
      </div>
    </div>
  );
};

export default SettingsPanel;