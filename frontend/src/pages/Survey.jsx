import { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  VStack,
  FormControl,
  FormLabel,
  Select,
  Button,
  useToast,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';

export default function Survey() {
  const [currentUser, setCurrentUser] = useState(null);
  const [userFromStorage, setUserFromStorage] = useState(null);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    const tempUserString = localStorage.getItem('tempUser');
    const parsed = tempUserString ? JSON.parse(tempUserString) : null;
    setUserFromStorage(parsed);
    setCurrentUser(parsed);
  }, []);

  const handleAnswer = (questionId, answer) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answer }));
  };

  const handleSubmit = async () => {
    const tempUserString = localStorage.getItem('tempUser');
    const parsedUser = tempUserString ? JSON.parse(tempUserString) : null;

    if (!parsedUser) {
      toast({
        title: 'User Error',
        description: 'Unable to retrieve registration info. Please re-register.',
        status: 'error',
        isClosable: true,
      });
      return;
    }

    if (Object.keys(answers).length < 6) {
      toast({
        title: 'Incomplete Survey',
        description: 'Please answer all 6 questions before submitting.',
        status: 'warning',
        isClosable: true,
      });
      return;
    }

    setLoading(true);
    try {
      const payload = {
        userId: String(parsedUser.user_id),
        answers: Object.entries(answers).map(([qid, ans]) => ({
          questionId: qid,
          answer: ans,
        })),
      };

      const res = await fetch('http://localhost:5000/api/survey/initial_submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || errorData.message || 'Server rejected the request.');
      }

      localStorage.removeItem('tempUser');

      toast({
        title: 'Survey Submitted Successfully!',
        description: 'Thank you for your feedback. Please log in to continue.',
        status: 'success',
        isClosable: true,
        duration: 3000,
      });

      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err) {
      toast({
        title: 'Submission failed.',
        description: err.message,
        status: 'error',
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  // ✅ 明确逻辑：初次加载，localStorage 也没有
  if (currentUser === null && !userFromStorage) {
    return (
      <Box textAlign="center" py={10} px={6}>
        <Alert status="error" role="alert">
          <AlertIcon />
          User information not found. Please start from the registration page.
        </Alert>
      </Box>
    );
  }

  return (
    <Box maxW="xl" mx="auto" mt={10} p={6} bg="white" borderRadius="lg" boxShadow="md">
      <Heading size="lg" mb={6}>User Onboarding Survey</Heading>
      <VStack spacing={5} align="stretch">
        {[...Array(6)].map((_, i) => (
          <FormControl key={i}>
            <FormLabel>
              {i + 1}
              .
              {' '}
              {[
                'What is your current level of experience in crypto investing?',
                'What is your primary objective when using this dashboard?',
                'What type of data do you find most useful?',
                'How frequently do you trade or rebalance your portfolio?',
                'Would you like to receive AML alerts when risk is detected?',
                'What is your biggest challenge in analyzing crypto markets?',
              ][i]}
            </FormLabel>
            <Select placeholder="Select" onChange={(e) => handleAnswer(`q${i + 1}`, e.target.value)}>
              {[
                ['beginner', 'intermediate', 'advanced'],
                ['monitor', 'invest', 'educate', 'compliance'],
                ['price', 'sentiment', 'aml', 'macro'],
                ['daily', 'weekly', 'monthly', 'longterm'],
                ['yes', 'no'],
                ['noise', 'timing', 'tools', 'understanding'],
              ][i].map((val) => (
                <option key={val} value={val}>{val}</option>
              ))}
            </Select>
          </FormControl>
        ))}
        <Button colorScheme="purple" onClick={handleSubmit} isLoading={loading}>
          Submit Survey
        </Button>
      </VStack>
    </Box>
  );
}
